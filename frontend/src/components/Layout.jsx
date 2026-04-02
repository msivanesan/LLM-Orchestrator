import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, LayoutDashboard, Users, UserPlus, LogOut, Key, MessageSquare, BookOpen, Sun, Moon
} from 'lucide-react';

const Layout = ({ user, onLogout, children, theme, toggleTheme }) => (
  <div className="app-layout">
    <aside className="sidebar">
      <div className="sidebar-brand">
        <ShieldCheck size={24} color="#E11D48" />
        <span>Darkny</span>
      </div>
      <nav className="sidebar-nav">
        <Link to="/users"><Users size={18} /> Users</Link>
        {user?.role === 'admin' && (
          <Link to="/keys"><Key size={18} /> API Keys</Link>
        )}
        <Link to="/settings"><ShieldCheck size={18} /> Settings</Link>
      </nav>
      <div className="sidebar-footer">
        <button onClick={onLogout}><LogOut size={18} /> Logout</button>
      </div>
    </aside>
    <main className="content-area">
      <header className="top-header">
        <button className="theme-toggle-btn" onClick={toggleTheme}>
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>
        <div className="user-profile-header">
          <div className="user-avatar-small">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <span>{user?.username || 'User'} ({user?.role || 'member'})</span>
        </div>
      </header>
      <div className="page-content">{children}</div>
    </main>
  </div>
);

export default Layout;
