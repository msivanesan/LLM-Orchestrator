import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import './index.css';

// API
import axios from 'axios';
import api, { ENDPOINTS } from './lib/api';

// Components
import Layout from './components/Layout';

// Pages
import HomePage from './pages/Home';
import LoginPage from './pages/Login';
import UserList from './pages/UserList';
import CreateUser from './pages/UserCreate';
import UserEdit from './pages/UserEdit';
import ManageProfile from './pages/ManageProfile';
import ForgotPassword from './pages/ForgotPassword';
import VerifyOTP from './pages/VerifyOTP';
import KeyList from './pages/KeyList';
import KeyCreate from './pages/KeyCreate';
import Chat from './pages/Chat';
import Docs from './pages/Docs';

function App() {
  const [user, setUser] = useState(null);
  const [bootstrapping, setBootstrapping] = useState(true);
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');

  // 🌙 Toggle Theme
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;
    root.className = theme;
    document.body.className = theme;
    root.style.transition = 'background-color 0.4s ease';
  }, [theme]);

  const handleLogout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      await api.delete('/logout');
      if (refreshToken) {
        await axios.delete(ENDPOINTS.LOGOUT_REFRESH, {
          headers: { Authorization: `Bearer ${refreshToken}` }
        });
      }
    } catch (err) {
      console.error("Token revocation failed", err);
    } finally {
      localStorage.clear();
      setUser(null);
      window.location.replace('/'); // Redirect to home and clear history stack
    }
  };


  const fetchSession = async () => {
    if (localStorage.getItem('access_token')) {
      try {
        const res = await api.get('/me');
        setUser(res.data);
      } catch (err) {
        localStorage.clear();
      }
    }
    setBootstrapping(false);
  };

  useEffect(() => {
    fetchSession();
  }, []);

  if (bootstrapping) {
    return (
      <div className="loader">
        <Loader2 className="animate-spin" /> 
        <span>Session Loading...</span>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={user ? <Navigate to="/" /> : <LoginPage onLogin={setUser} theme={theme} toggleTheme={toggleTheme} />} 
        />
        
        {/* Admin Only Identity Routes */}
        <Route 
          path="/users" 
          element={user?.role === 'admin' ? <Layout user={user} onLogout={handleLogout} theme={theme} toggleTheme={toggleTheme}><UserList /></Layout> : (user ? <Navigate to="/chat" /> : <Navigate to="/login" />)} 
        />
        <Route 
          path="/users/create" 
          element={user?.role === 'admin' ? <Layout user={user} onLogout={handleLogout} theme={theme} toggleTheme={toggleTheme}><CreateUser /></Layout> : (user ? <Navigate to="/chat" /> : <Navigate to="/login" />)} 
        />
        <Route 
          path="/users/edit/:id" 
          element={user?.role === 'admin' ? <Layout user={user} onLogout={handleLogout} theme={theme} toggleTheme={toggleTheme}><UserEdit /></Layout> : (user ? <Navigate to="/chat" /> : <Navigate to="/login" />)} 
        />
        
        {/* Protected Settings (All Users) */}
        <Route 
          path="/settings" 
          element={user ? <Layout user={user} onLogout={handleLogout} theme={theme} toggleTheme={toggleTheme}><ManageProfile /></Layout> : <Navigate to="/login" />} 
        />
        
        {/* Admin Only API Key Routes */}
        <Route 
          path="/keys" 
          element={user?.role === 'admin' ? <Layout user={user} onLogout={handleLogout} theme={theme} toggleTheme={toggleTheme}><KeyList /></Layout> : (user ? <Navigate to="/chat" /> : <Navigate to="/login" />)} 
        />
        <Route 
          path="/keys/create" 
          element={user?.role === 'admin' ? <Layout user={user} onLogout={handleLogout} theme={theme} toggleTheme={toggleTheme}><KeyCreate /></Layout> : (user ? <Navigate to="/chat" /> : <Navigate to="/login" />)} 
        />

        
        {/* Chat Route */}
        <Route
          path="/chat/:sessionId?"
          element={user ? <Layout user={user} onLogout={handleLogout} theme={theme} toggleTheme={toggleTheme}><Chat user={user} /></Layout> : <Navigate to="/login" />}
        />

        <Route
          path="/docs"
          element={<Docs theme={theme} toggleTheme={toggleTheme} />}
        />
        
        {/* Public Password Recovery Routes */}
        <Route path="/forgot-password" element={<ForgotPassword theme={theme} toggleTheme={toggleTheme} />} />
        <Route path="/verify-otp" element={<VerifyOTP theme={theme} toggleTheme={toggleTheme} />} />
        
        <Route path="/" element={user ? <Navigate to={user.role === 'admin' ? "/users" : "/chat"} /> : <HomePage theme={theme} toggleTheme={toggleTheme} />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
