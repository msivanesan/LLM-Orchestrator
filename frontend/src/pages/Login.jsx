import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Key, User, Lock, Loader2, Moon, Sun } from 'lucide-react';
import api from '../lib/api';

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
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('refresh_token', res.data.refresh_token);
      if (res.status === 200) {
        onLogin(res.data.user);
        // 🚀 SMART REDIRECT BASED ON ROLE
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
    <div className="container" style={{ marginTop: '10vh', position: 'relative' }}>
      <header style={{ position: 'absolute', top: '1.5rem', right: '1.5rem' }}>
        <button className="theme-toggle-btn" onClick={toggleTheme}>
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>
      </header>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <Key size={40} color="#E11D48" style={{ marginBottom: '1rem' }} />
        <h1>Darkny</h1>
        <p className="subtitle">Sign in to your AI Orchestrator</p>
      </div>
      
      <form onSubmit={handleLogin}>
        <div className="form-group">
          <label>Username</label>
          <div className="input-wrapper">
            <User />
            <input 
              type="text" 
              placeholder="Username" 
              required 
              value={formData.username}
              onChange={e => setFormData({...formData, username: e.target.value})} 
            />
          </div>
        </div>
        <div className="form-group">
          <label>Password</label>
          <div className="input-wrapper">
            <Lock />
            <input 
              type="password" 
              placeholder="••••••••" 
              required 
              value={formData.password}
              onChange={e => setFormData({...formData, password: e.target.value})} 
            />
          </div>
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? <Loader2 className="animate-spin" /> : 'Login'}
        </button>
        
        <div style={{ textAlign: 'right', marginTop: '1rem' }}>
          <Link to="/forgot-password" style={{ color: '#E11D48', textDecoration: 'none', fontSize: '0.875rem' }}>
            Forgot Password?
          </Link>
        </div>
        
        {feedback.message && (
          <div className={`feedback ${feedback.type}`}>{feedback.message}</div>
        )}
      </form>
    </div>
  );
};

export default LoginPage;
