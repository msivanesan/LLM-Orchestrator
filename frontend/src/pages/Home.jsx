import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, ArrowRight, BookOpen, LogIn, Sun, Moon } from 'lucide-react';

const HomePage = ({ theme, toggleTheme }) => {
  return (
    <div className="home-container">
      {/* 💎 Glass Navbar */}
      <nav className="home-nav">
        <div className="home-brand">
          <ShieldCheck color="#E11D48" size={32} />
          <span>Darkny</span>
        </div>
        <div className="home-nav-links">
          <Link to="/docs" className="nav-link">
            <BookOpen size={18} />
            Docs
          </Link>
          <button className="theme-toggle-btn" onClick={toggleTheme}>
            {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
          </button>
          <Link to="/login" className="nav-login-btn">
            Sign In
            <LogIn size={18} />
          </Link>
        </div>
      </nav>

      {/* 🚀 Hero Section */}
      <header className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">Next-Gen AI Management</div>
          <h1>Orchestrate Your <span>AI Workforce</span> With Precision</h1>
          <p>
            The premium, enterprise-grade orchestrator for large language models. 
            Manage users, deploy API keys, and monitor your AI nodes in one sleek, 
            glass-encrypted interface.
          </p>
          <div className="hero-actions">
            <Link to="/login" className="hero-primary-btn">
              Get Started <ArrowRight size={20} />
            </Link>
            <Link to="/docs" className="hero-secondary-btn">
              View Documentation
            </Link>
          </div>
        </div>
        <div className="hero-visual">
           {/* Floating Glass Cards to show off the UI theme */}
           <div className="glass-card-float c1"></div>
           <div className="glass-card-float c2"></div>
        </div>
      </header>
    </div>
  );
};

export default HomePage;
