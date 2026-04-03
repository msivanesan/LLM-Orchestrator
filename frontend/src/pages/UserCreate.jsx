import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  UserPlus, Mail, Lock, Loader2, ShieldCheck, 
  ArrowLeft, Terminal, User, Shield, Key
} from 'lucide-react';
import api from '../lib/api';

const CreateUser = () => {
  const [formData, setFormData] = useState({ username: '', email: '', password: '', role: 'user' });
  const [feedback, setFeedback] = useState({ message: '', type: '' });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setFeedback({ message: '', type: '' });
    try {
      await api.post('/register', formData);
      setFeedback({ message: "Provisioning Complete: Node identity assigned successfully.", type: 'success' });
      setTimeout(() => navigate('/users'), 1500);
    } catch (err) {
      setFeedback({ message: err.response?.data?.message || "Provisioning Failed: Check system registry.", type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="provision-workspace">
      {/* 🔮 Aesthetic Background Elements (Scoped to this page) */}
      <div className="pg-blob pg-b1"></div>
      <div className="pg-blob pg-b2"></div>

      <div className="provision-split">
        {/* 🎨 Left Side - Branded Visual (Reference to Login) */}
        <div className="provision-visual-side">
          <div className="visual-content-compact">
            <div className="floating-badge-v2">
              <ShieldCheck size={18} />
              <span>Provisioning Protocol Enabled</span>
            </div>
            <h2>Register a <span>Darkny</span> Node</h2>
            <p>Provision new secure identities with high-density privilege management.</p>
            
            <div className="terminal-preview-mini">
              <div className="term-header">
                <div className="dot red"></div><div className="dot yellow"></div><div className="dot green"></div>
                <span>provision_service.sh</span>
              </div>
              <div className="term-body-compact">
                <div className="term-line"><span>$</span> init_identity --role={formData.role}</div>
                <div className="term-line"><span>&gt;</span> generating_node_id...</div>
                <div className="term-line success"><span>✓</span> Buffer allocated (12ms)</div>
              </div>
            </div>

            <div className="provision-stats-ribbon">
              <div className="stat-unit">
                <div className="stat-val">256-bit</div>
                <div className="stat-lab">Encryption</div>
              </div>
              <div className="stat-unit">
                <div className="stat-val">Active</div>
                <div className="stat-lab">Registry</div>
              </div>
            </div>
          </div>
        </div>

        {/* 🔐 Right Side - Provisioning Form */}
        <div className="provision-form-side">
          <div className="provision-glass-card">
            <div className="provision-header">
              <div className="provision-logo-ring">
                <UserPlus size={28} color="var(--primary)" />
              </div>
              <h3>New Identity Provision</h3>
              <p>Configure the credentials for the new system operator.</p>
            </div>

            <form onSubmit={handleSubmit} className="provision-form-modern">
               <div className="form-group-saas">
                <label>Operator Identifier</label>
                <div className="input-field-saas">
                  <User size={18} />
                  <input 
                    type="text" 
                    placeholder="New Username" 
                    required 
                    value={formData.username}
                    onChange={e => setFormData({...formData, username: e.target.value})} 
                  />
                </div>
              </div>

              <div className="form-group-saas">
                <label>Communication End-point</label>
                <div className="input-field-saas">
                  <Mail size={18} />
                  <input 
                    type="email" 
                    placeholder="email@example.com" 
                    required 
                    value={formData.email}
                    onChange={e => setFormData({...formData, email: e.target.value})} 
                  />
                </div>
              </div>

              <div className="form-group-saas">
                <label>Master Security Pass</label>
                <div className="input-field-saas">
                  <Key size={18} />
                  <input 
                    type="password" 
                    placeholder="••••••••" 
                    required 
                    value={formData.password}
                    onChange={e => setFormData({...formData, password: e.target.value})} 
                  />
                </div>
              </div>

              <div className="form-group-saas">
                <label>Primary Privilege Tier</label>
                <div className="role-chip-group">
                  <button 
                    type="button" 
                    className={`role-chip ${formData.role === 'user' ? 'active' : ''}`}
                    onClick={() => setFormData({...formData, role: 'user'})}
                  >
                    <User size={16} /> Standard
                  </button>
                  <button 
                    type="button" 
                    className={`role-chip ${formData.role === 'admin' ? 'active' : ''}`}
                    onClick={() => setFormData({...formData, role: 'admin'})}
                  >
                    <Shield size={16} /> Admin
                  </button>
                </div>
              </div>

              <button type="submit" className="provision-submit-btn" disabled={loading}>
                {loading ? <Loader2 className="animate-spin" /> : <>Finalize Provisioning <ArrowLeft className="rotate-180" size={18} /></>}
              </button>

              {feedback.message && (
                <div className={`notification-modern ${feedback.type}`}>
                  <div className="notif-dot"></div>
                  {feedback.message}
                </div>
              )}
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateUser;
