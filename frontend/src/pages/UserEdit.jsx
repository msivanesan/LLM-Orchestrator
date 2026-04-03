import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Loader2, Save, X, User, Mail, Shield, 
  ChevronLeft, AlertCircle, CheckCircle2,
  Lock, ArrowRight, ShieldCheck, Activity
} from 'lucide-react';
import api from '../lib/api';

const UserEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    role: 'user',
    is_active: true
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await api.get(`/${id}`);
        setFormData({
          username: res.data.username,
          email: res.data.email,
          role: res.data.role,
          is_active: res.data.is_active
        });
      } catch (err) {
        console.error(err);
        setMessage({ type: 'error', text: 'Error loading user data. Please refresh.' });
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      await api.put(`/${id}`, formData);
      setMessage({ type: 'success', text: 'User account updated successfully.' });
      setTimeout(() => navigate('/users'), 1500);
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.message || 'Failed to update user.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) return (
    <div className="loader-container-full">
      <Loader2 className="animate-spin" size={32} color="var(--primary)" />
      <span>Loading user details...</span>
    </div>
  );

  return (
    <div className="console-workspace-unified">
      {/* 🧭 NAVIGATION HEADER */}
      <header className="unified-console-header-v2">
        <div className="header-nav-main">
          <button className="back-nav-btn" onClick={() => navigate('/users')}>
            <ChevronLeft size={20} />
          </button>
          <div className="header-nav-info">
            <h1>Edit User</h1>
            <div className="header-nav-breadcrumb">
              <span>Users</span>
              <ArrowRight size={12} />
              <span className="current">{formData.username || '...'}</span>
            </div>
          </div>
        </div>
        
        <div className="header-nav-actions">
           <button type="button" className="btn-ghost-modern" onClick={() => navigate('/users')}>
              Cancel
            </button>
            <button form="edit-user-form" type="submit" className="btn-primary-v2" disabled={saving}>
              {saving ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
        </div>
      </header>

      {/* 📄 MAIN CONTENT AREA */}
      <div className="datagrid-container-v2 scroll-y-auto">
        <form id="edit-user-form" onSubmit={handleSubmit} className="modern-saas-form">
          
          <div className="form-section-modern">
            <div className="form-section-info">
              <h3>General Information</h3>
              <p>Update personal details and identification across the system.</p>
            </div>
            
            <div className="form-section-inputs">
              <div className="form-row-modern">
                <label>Username</label>
                <div className="input-group-modern">
                  <User size={16} className="input-icon-v2" />
                  <input 
                    type="text" 
                    value={formData.username}
                    onChange={e => setFormData({...formData, username: e.target.value})}
                    placeholder="Username"
                    required 
                  />
                </div>
              </div>

              <div className="form-row-modern">
                <label>Email Address</label>
                <div className="input-group-modern">
                  <Mail size={16} className="input-icon-v2" />
                  <input 
                    type="email" 
                    value={formData.email}
                    onChange={e => setFormData({...formData, email: e.target.value})}
                    placeholder="email@example.com"
                    required 
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="form-divider-modern"></div>

          <div className="form-section-modern">
            <div className="form-section-info">
              <h3>Permissions & Status</h3>
              <p>Manage access levels and account activity status.</p>
            </div>

            <div className="form-section-inputs">
              <div className="form-row-modern">
                <label>User Role</label>
                <div className="role-selector-modern">
                  <button 
                    type="button" 
                    className={formData.role === 'user' ? 'active' : ''} 
                    onClick={() => setFormData({...formData, role: 'user'})}
                  >
                    <Shield size={16} />
                    <span>User</span>
                  </button>
                  <button 
                    type="button" 
                    className={formData.role === 'admin' ? 'active' : ''} 
                    onClick={() => setFormData({...formData, role: 'admin'})}
                  >
                    <ShieldCheck size={16} />
                    <span>Admin</span>
                  </button>
                </div>
                <p className="field-help-text">Admins have full access to system settings and management.</p>
              </div>

              <div className="form-row-modern">
                <label>Account Status</label>
                <div 
                  className={`saas-status-toggle ${formData.is_active ? 'on' : 'off'}`}
                  onClick={() => setFormData({...formData, is_active: !formData.is_active})}
                >
                  <div className="toggle-thumb"></div>
                  <span>{formData.is_active ? 'Active' : 'Disabled'}</span>
                </div>
                <p className="field-help-text">Disabled users cannot log in or perform any actions.</p>
              </div>
            </div>
          </div>

          {message && (
            <div className={`notification-banner-modern ${message.type}`}>
              {message.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
              <span>{message.text}</span>
            </div>
          )}

        </form>
      </div>
    </div>
  );
};

export default UserEdit;
