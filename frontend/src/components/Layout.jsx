import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  ShieldCheck, Users, Key, MessageSquare, LogOut, Sun, Moon
} from 'lucide-react';
import logoImg from '../assets/logo.png';
import faviconImg from '../assets/logofav.png';

const Layout = ({ user, onLogout, children, theme, toggleTheme }) => {
  const location = useLocation();
  const isChatPage = location.pathname.startsWith('/chat');
  
  return (
    <div className={`app-layout ${isChatPage ? 'chat-mini-mode' : ''}`}>
      {/* 🏛️ Operative Console Sidebar */}

      {isChatPage ? (
        <aside className="chat-mini-sidebar">
          <div className="mini-sidebar-top">
            <div className="brand-icon-ring mini">
              <img src={faviconImg} alt="Darkny" className="mini-sidebar-logo-img" />
            </div>
          </div>

          <div className="mini-sidebar-bottom">
            {user?.role === 'admin' && (
              <Link to="/users" className="mini-nav-item" title="Back to Admin Dashboard">
                <Users size={20} />
              </Link>
            )}
            <Link to="/settings" className="mini-nav-item" title="Settings">
              <ShieldCheck size={20} />
            </Link>
            <div className="mini-sep"></div>
            <div className="user-avatar-mini" title={user?.username}>
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            <button className="mini-logout-btn" onClick={onLogout} title="Sign Out">
              <LogOut size={20} />
            </button>
          </div>
        </aside>
      ) : (
        <aside className="sidebar">
          <div className="sidebar-brand-container">
            <div className="sidebar-brand">
              <img src={logoImg} alt="Darkny" className="sidebar-brand-logo" />
          </div>
            
            <button className="sidebar-theme-toggle" onClick={toggleTheme} title="Toggle Theme">
              {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
            </button>
          </div>

          <nav className="sidebar-nav">
            {user?.role === 'admin' && (
              <>
                <Link to="/users" className={location.pathname.startsWith('/users') ? 'active' : ''}>
                  <Users size={18} /> 
                  <span>Users</span>
                </Link>
                <Link to="/keys" className={location.pathname.startsWith('/keys') ? 'active' : ''}>
                  <Key size={18} /> 
                  <span>Secure Keys</span>
                </Link>
              </>
            )}
            <Link to="/chat" className={location.pathname === '/chat' ? 'active' : ''}>
              <MessageSquare size={18} /> 
              <span>Chat Hub</span>
            </Link>
            <Link to="/settings" className={location.pathname === '/settings' ? 'active' : ''}>
              <ShieldCheck size={18} /> 
              <span>Settings</span>
            </Link>
          </nav>

          <div className="sidebar-footer">
            <div className="sidebar-user-card">
              <div className="user-avatar-small">{user?.username?.charAt(0).toUpperCase()}</div>
              <div className="user-details">
                <span className="user-name">{user?.username}</span>
                <span className="user-role-tag">{user?.role}</span>
              </div>
            </div>
            <button className="logout-btn" onClick={onLogout}>
              <LogOut size={16} /> 
              <span>Sign Out</span>
            </button>
          </div>
        </aside>
      )}

      {/* 🚀 operative Area (Adapts to Mini Sidebar) */}
      <main className="content-area-clean">
        <div className="scrollable-content-wrap-wide">
          <div className="page-content-modern">{children}</div>
        </div>
      </main>
    </div>
  );
};



export default Layout;
