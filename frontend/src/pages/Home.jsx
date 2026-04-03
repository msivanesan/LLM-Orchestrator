import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, ArrowRight, BookOpen, LogIn, Sun, Moon, 
  Zap, Shield, Brain, Activity, Globe, Cpu, ChevronRight
} from 'lucide-react';
import logoImg from '../assets/logo.png';

const HomePage = ({ theme, toggleTheme }) => {
  return (
    <div className="home-container">
      {/* 🌌 Background Blobs for Atmosphere */}
      <div className="bg-blob blob-1"></div>
      <div className="bg-blob blob-2"></div>

      {/* 💎 Premium Glass Navbar */}
      <nav className="home-nav">
        <div className="home-brand">
          <img src={logoImg} alt="Darkny" className="home-nav-logo" />
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

      {/* 🚀 Immersive Hero Section */}
      <header className="hero-section-wide">
        <div className="hero-content-modern">
          <div className="hero-badge-glow">
            <Zap size={14} fill="currentColor" />
            <span>v1.2 Stable Release</span>
          </div>
          <h1>Orchestrate Your <span>AI workforce</span> With Absolute Precision</h1>
          <p>
            The production-grade ecosystem for secure AI model orchestration, centralized identity, 
            and persistent LLM memory. Built for scale, designed for stability.
          </p>
          <div className="hero-actions-row">
            <Link to="/login" className="hero-primary-btn">
              Launch Console <ArrowRight size={20} />
            </Link>
            <Link to="/docs" className="hero-outline-btn">
              Read Documentation
            </Link>
          </div>
          
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-val">99.9%</span>
              <span className="stat-label">Uptime</span>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <span className="stat-val">5ms</span>
              <span className="stat-label">Latency</span>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <span className="stat-val">256+</span>
              <span className="stat-label">Models</span>
            </div>
          </div>
        </div>

        <div className="hero-visual-container">
          <div className="floating-card c1">
            <div className="card-header"><Brain size={16} /> <span>Query Engine</span></div>
            <div className="card-line"></div>
            <div className="card-line short"></div>
          </div>
          <div className="floating-card c2">
            <div className="card-header"><Shield size={16} /> <span>Auth Sidecar</span></div>
            <div className="card-pill">Active</div>
          </div>
          <div className="floating-card c3">
            <div className="card-header"><Activity size={16} /> <span>APM Live</span></div>
            <div className="card-graph">
              <span></span><span></span><span></span><span></span>
            </div>
          </div>
          <div className="orb-glow"></div>
        </div>
      </header>

      {/* 🌀 Scroll Down Indicator */}
      <div className="scroll-indicator">
        <span>Discover Features</span>
        <div className="mouse"></div>
      </div>

      {/* 🛠️ Features Grid */}
      <section className="features-section">
        <div className="section-header">
          <span className="section-tag">Core Capabilities</span>
          <h2>A Unified Platform for <span>Enterprise AI</span></h2>
        </div>

        <div className="features-grid-modern">
          <div className="feature-card-premium">
            <div className="feature-icon-wrapper"><Cpu size={24} /></div>
            <h3>Model Gateway</h3>
            <p>Deploy and orchestrate local LLMs (Ollama/vLLM) with role-based model enforcement.</p>
            <Link to="/docs#models" className="feature-link">Learn more <ChevronRight size={14} /></Link>
          </div>

          <div className="feature-card-premium">
            <div className="feature-icon-wrapper"><ShieldCheck size={24} /></div>
            <h3>Security Sidecar</h3>
            <p>Nginx-powered gateway with integrated API key validation and rate limiting.</p>
            <Link to="/docs#auth" className="feature-link">Learn more <ChevronRight size={14} /></Link>
          </div>

          <div className="feature-card-premium">
            <div className="feature-icon-wrapper"><Brain size={24} /></div>
            <h3>RAG Memory</h3>
            <p>Persistent conversation state and fact extraction with integrated ChromaDB support.</p>
            <Link to="/docs#embed" className="feature-link">Learn more <ChevronRight size={14} /></Link>
          </div>

          <div className="feature-card-premium">
            <div className="feature-icon-wrapper"><Globe size={24} /></div>
            <h3>Observability</h3>
            <p>Full APM stack with Prometheus and Grafana for real-time performance tracking.</p>
            <Link to="/docs#monitoring" className="feature-link">Learn more <ChevronRight size={14} /></Link>
          </div>
        </div>
      </section>

      {/* 🚀 CTA Section */}
      <section className="cta-banner">
        <div className="cta-content">
          <h2>Ready to scale your AI fleet?</h2>
          <p>Get started today with the industry's most stable orchestration layer.</p>
          <Link to="/login" className="cta-btn">Create Your First Instance</Link>
        </div>
      </section>

      {/* 🏮 Footer */}
      <footer className="home-footer">
        <div className="footer-top">
          <div className="footer-brand">
            <img src={logoImg} alt="Darkny" className="footer-nav-logo" />
          </div>
          <div className="footer-links">
            <Link to="/docs">Documentation</Link>
            <a href="https://github.com/msivanesan/LLM-Orchestrator">Github</a>
            <Link to="/login">Console</Link>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2026 Darkny AI Orchestration Infrastructure. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
