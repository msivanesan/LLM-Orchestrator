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
import LoginPage from './pages/Login';
import DashboardHome from './pages/Dashboard';
import UserList from './pages/UserList';
import CreateUser from './pages/UserCreate';
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

  const handleLogout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      // Revoke Access Token
      await api.delete('/logout');
      // Revoke Refresh Token
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
          element={user ? <Navigate to="/dashboard" /> : <LoginPage onLogin={setUser} />} 
        />
        
        {/* Protected Routes */}
        <Route 
          path="/dashboard" 
          element={user ? <Layout user={user} onLogout={handleLogout}><DashboardHome user={user} /></Layout> : <Navigate to="/login" />} 
        />
        <Route 
          path="/users" 
          element={user ? <Layout user={user} onLogout={handleLogout}><UserList /></Layout> : <Navigate to="/login" />} 
        />
        <Route 
          path="/users/create" 
          element={user ? <Layout user={user} onLogout={handleLogout}><CreateUser /></Layout> : <Navigate to="/login" />} 
        />
        <Route 
          path="/settings" 
          element={user ? <Layout user={user} onLogout={handleLogout}><ManageProfile /></Layout> : <Navigate to="/login" />} 
        />
        
        {/* Admin Only API Key Routes */}
        <Route 
          path="/keys" 
          element={user?.role === 'admin' ? <Layout user={user} onLogout={handleLogout}><KeyList /></Layout> : <Navigate to="/" />} 
        />
        <Route 
          path="/keys/create" 
          element={user?.role === 'admin' ? <Layout user={user} onLogout={handleLogout}><KeyCreate /></Layout> : <Navigate to="/" />} 
        />
        
        {/* Chat Route */}
        <Route
          path="/chat"
          element={user ? <Chat user={user} /> : <Navigate to="/login" />}
        />
        <Route
          path="/docs"
          element={<Docs />}
        />
        
        {/* Public Password Recovery Routes */}
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/verify-otp" element={<VerifyOTP />} />
        
        <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
