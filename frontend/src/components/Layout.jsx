import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, LayoutDashboard, Users, UserPlus, LogOut, Key, MessageSquare
} from 'lucide-react';

const Layout = ({ user, onLogout, children }) => (
  <div className="app-layout">
    <aside className="sidebar">
      <div className="sidebar-brand">
        <ShieldCheck size={24} color="#6366f1" />
        <span>Admin Panel</span>
      </div>
      <nav className="sidebar-nav">
        <Link to="/dashboard"><LayoutDashboard size={18} /> Dashboard</Link>
        <Link to="/chat"><MessageSquare size={18} /> AI Chat</Link>
        <Link to="/users"><Users size={18} /> Users</Link>
        {user.role === 'admin' && (
          <>
            <Link to="/keys"><Key size={18} /> API Keys</Link>
            <Link to="/users/create"><UserPlus size={18} /> Add User</Link>
          </>
        )}
        <Link to="/settings"><ShieldCheck size={18} /> Settings</Link>
      </nav>
      <div className="sidebar-footer">
        <button onClick={onLogout}><LogOut size={18} /> Logout</button>
      </div>
    </aside>
    <main className="content-area">
      <header className="top-header">
        <div className="user-profile-header">
          <div className="user-avatar-small">{user.username.charAt(0).toUpperCase()}</div>
          <span>{user.username} ({user.role})</span>
        </div>
      </header>
      <div className="page-content">{children}</div>
    </main>
  </div>
);

export default Layout;
