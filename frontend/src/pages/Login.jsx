import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Lock, Loader2, Moon, Sun, ArrowLeft, Terminal } from 'lucide-react';
import api from '../lib/api';
import logoImg from '../assets/logo.png';
import faviconImg from '../assets/logofav.png';

const LoginPage = ({ onLogin, theme, toggleTheme }) => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [feedback, setFeedback] = useState({ message: '', type: '' });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setFeedback({ message: '', type: '' });
    try {
      const res = await api.post('/login', { username: formData.username, password: formData.password });
      if (res.status === 200) {
        localStorage.setItem('access_token', res.data.access_token);
        localStorage.setItem('refresh_token', res.data.refresh_token);
        onLogin(res.data.user);
        const role = res.data.user.role;
        if (role === 'admin') {
          navigate('/users');
        } else {
          navigate('/chat');
        }
      }
    } catch (err) {
      setFeedback({ message: err.response?.data?.message || 'Login failed', type: 'error' });
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="login-master-container">
      {/* 🎆 Deep Background Glows */}
      <div className="bg-blob-login blob-l1"></div>
      <div className="bg-blob-login blob-l2"></div>

      {/* 🔙 Back to Site */}
      <Link to="/" className="back-link">
        <ArrowLeft size={18} />
        <span>Back to Website</span>
      </Link>

      <div className="login-split">
        {/* 🎨 Left Side - Branded Visual */}
        <div className="login-visual-side">
          <div className="visual-content">
            <img src={logoImg} alt="Darkny" className="login-brand-logo" />
            <p>Manage your enterprise AI nodes with encrypted precision and real-time observability.</p>
            
            <div className="terminal-preview">
              <div className="term-header">
                <div className="dot"></div><div className="dot"></div><div className="dot"></div>
                <span>auth_gateway.log</span>
              </div>
              <div className="term-body">
                <div className="term-line"><span>$</span> init_handshake --node=AI-Core-01</div>
                <div className="term-line success"><span>✓</span> Identity verified (03ms)</div>
                <div className="term-line"><span>$</span> establishing_session...</div>
              </div>
            </div>
          </div>
        </div>

        {/* 🔐 Right Side - Login Form */}
        <div className="login-form-side">
          <div className="login-glass-card">
            <header className="login-header-controls">
              <button className="theme-toggle-btn" onClick={toggleTheme}>
                {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
              </button>
            </header>

            <div className="login-card-top">
              <div className="login-logo-ring">
                <img src={faviconImg} alt="Darkny" className="login-card-symbol" />
              </div>
              <h2>Sign In</h2>
              <p>Welcome back! Enter your developer credentials.</p>
            </div>

            <form onSubmit={handleLogin} className="login-form">
              <div className="form-group-modern">
                <label>Developer ID</label>
                <div className="input-group-modern">
                  <User size={18} />
                  <input 
                    type="text" 
                    placeholder="Username" 
                    required 
                    value={formData.username}
                    onChange={e => setFormData({...formData, username: e.target.value})} 
                  />
                </div>
              </div>

              <div className="form-group-modern">
                <label>Security Key</label>
                <div className="input-group-modern">
                  <Lock size={18} />
                  <input 
                    type="password" 
                    placeholder="••••••••" 
                    required 
                    value={formData.password}
                    onChange={e => setFormData({...formData, password: e.target.value})} 
                  />
                </div>
              </div>

              <div className="login-actions-util">
                <Link to="/forgot-password">Security Recovery?</Link>
              </div>

              <button type="submit" className="login-submit-btn" disabled={loading}>
                {loading ? <Loader2 className="animate-spin" /> : <>Access Console <ArrowLeft className="rotate-180" size={18} /></>}
              </button>

              {feedback.message && (
                <div className={`feedback ${feedback.type}`}>{feedback.message}</div>
              )}
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
