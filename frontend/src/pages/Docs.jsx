import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowLeft, Copy, AlertTriangle, 
  Search, Sun, Moon, Check, Terminal, ExternalLink 
} from 'lucide-react';
import logoImg from '../assets/logo.png';
import './Docs.css'; // Use specialized CSS for docs

const Documentation = ({ theme, toggleTheme }) => {
  const [activeSection, setActiveSection] = useState('introduction');
  const [copiedId, setCopiedId] = useState(null);

  // 📋 Copy to Clipboard Handler
  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // 🔦 Scroll Observer for TOC Highlight
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        });
      },
      { rootMargin: '-10% 0px -80% 0px' }
    );

    const sections = document.querySelectorAll('section[id], h2[id]');
    sections.forEach((section) => observer.observe(section));

    return () => sections.forEach((section) => observer.unobserve(section));
  }, []);

  const menuGroups = [
    {
      title: 'Getting Started',
      items: [
        { id: 'introduction', label: 'Introduction' },
        { id: 'auth', label: 'Authentication' },
      ]
    },
    {
      title: 'Endpoints',
      items: [
        { id: 'models', label: 'Model Discovery' },
        { id: 'generate', label: 'Text Generation' },
        { id: 'embed', label: 'Semantic Search' },
      ]
    },
    {
      title: 'Security',
      items: [
        { id: 'rejections', label: 'Role Enforcement' },
        { id: 'errors', label: 'Error Codes' },
      ]
    }
  ];

  return (
    <div className="docs-master-layout">
      {/* 📘 Documentation Sidebar */}
      <aside className="docs-sidebar">
        <div className="docs-sidebar-inner">
          <div className="docs-logo">
            <Link to="/" className="brand-logo">
              <img src={logoImg} alt="Darkny" className="docs-brand-logo-img" />
            </Link>
            <button className="theme-toggle-btn" onClick={toggleTheme} title="Toggle Theme">
              {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            </button>

          </div>

          <div className="docs-search-container">
            <Search size={16} className="search-icon" />
            <input type="text" placeholder="Search documentation..." readOnly disabled />
          </div>

          <nav className="docs-menu">
            {menuGroups.map((group, idx) => (
              <div key={idx} className="docs-menu-group">
                <span className="group-title">{group.title}</span>
                {group.items.map(item => (
                  <a 
                    key={item.id} 
                    href={`#${item.id}`} 
                    className={activeSection === item.id ? 'active' : ''}
                    onClick={(e) => {
                      e.preventDefault();
                      document.getElementById(item.id)?.scrollIntoView({ behavior: 'smooth' });
                    }}
                  >
                    {item.label}
                  </a>
                ))}
              </div>
            ))}
          </nav>
          
          <div className="docs-sidebar-footer">
            <a href="https://github.com/msivanesan/LLM-Orchestrator" target="_blank" rel="noreferrer">
              <ExternalLink size={14} /> Open Repository
            </a>
          </div>
        </div>
      </aside>

      {/* 📄 Main Content Area */}
      <main className="docs-main">
        <header className="docs-topbar">
           <Link to="/" className="docs-back-link">
             <ArrowLeft size={16} /> <span>Back to Console</span>
           </Link>
           <div className="docs-actions">
              <span className="version-pill">v1.2.0-stable</span>
           </div>
        </header>

        <div className="docs-article-wrapper">
          <section id="introduction" className="docs-section">
            <div className="content-badge">Getting Started / Introduction</div>
            <h1>AI Gateway <span>Guidance</span></h1>
            <p className="lead-text">
              Welcome to the Darkny AI Gateway. This documentation provides technical guidance for 
              external agents and developers connecting to our high-performance model orchestration layer.
            </p>

            <h2 id="auth">Authentication</h2>
            <p>
              All requests to the Darkny Gateway must include your designated API key. Unlike traditional 
              APIs, the gateway uses a specific header for model-layer security.
            </p>

            <div className="callout callout-danger">
               <AlertTriangle size={20} className="callout-icon" />
               <div className="callout-body">
                 <strong>IMPORTANT:</strong> Do not use <code>Bearer</code> tokens. The gateway specifically 
                 expects the <code>X-API-KEY</code> header for validation.
               </div>
            </div>

            <div className="property-grid">
               <div className="property-header">
                  <span className="label">Required Headers</span>
               </div>
               <div className="property-row">
                  <div className="prop-name">X-API-KEY</div>
                  <div className="prop-example">ak_your_key_here</div>
                  <button 
                    className="copy-minimal" 
                    onClick={() => handleCopy('X-API-KEY: ak_your_key_here', 'h1')}
                    title="Copy Header Entry"
                  >
                    {copiedId === 'h1' ? <Check size={12} color="var(--success)" /> : <Copy size={12} />}
                  </button>
               </div>
               <div className="property-row">
                  <div className="prop-name">Content-Type</div>
                  <div className="prop-example">application/json</div>
                  <button 
                    className="copy-minimal" 
                    onClick={() => handleCopy('application/json', 'h2')}
                    title="Copy Type"
                  >
                    {copiedId === 'h2' ? <Check size={12} color="var(--success)" /> : <Copy size={12} />}
                  </button>
               </div>
            </div>
          </section>

          <hr className="docs-divider" />

          <section id="models" className="docs-section">
            <h2>1. Model Discovery</h2>
            <p>
              Retrieve a live list of available models and their current capabilities (Generative vs. Embedding).
            </p>
            <div className="endpoint-pill">
              <span className="method get">GET</span>
              <code className="path">/api/ai/models</code>
            </div>

            <div className="code-block-modern">
               <div className="code-block-header">
                  <div className="code-lang"><Terminal size={14} /> cURL Request</div>
                  <button 
                    className="copy-btn-modern" 
                    onClick={() => handleCopy('curl -X GET http://<gateway-ip>/api/ai/models -H "X-API-KEY: ak_..."', 'c1')}
                  >
                    {copiedId === 'c1' ? <><Check size={14} /> Copied</> : <><Copy size={14} /> Copy Code</>}
                  </button>
               </div>
               <pre><code>{`curl -X GET http://<gateway-ip>/api/ai/models \\
     -H "X-API-KEY: ak_..."`}</code></pre>
            </div>
          </section>

          <section id="generate" className="docs-section">
            <h2>2. Generative AI (Text)</h2>
            <p>
              Use this endpoint for chat, reasoning, or content creation. Only generative models 
              (e.g., <code>llama3</code>, <code>tinyllama</code>) are permitted here.
            </p>
            <div className="endpoint-pill">
              <span className="method post">POST</span>
              <code className="path">/api/ai/models/&lt;model_id&gt;/generate</code>
            </div>

            <div className="property-grid">
               <div className="property-header">
                  <span className="label">Request Parameters</span>
                  <span className="label-secondary">Body (JSON)</span>
               </div>
               <div className="property-row-detailed">
                  <div className="prop-meta">
                    <span className="name">messages</span>
                    <span className="type">array</span>
                    <span className="req">Required</span>
                  </div>
                  <div className="prop-desc">Array of message objects (role/content)</div>
               </div>
               <div className="property-row-detailed">
                  <div className="prop-meta">
                    <span className="name">temperature</span>
                    <span className="type">float</span>
                  </div>
                  <div className="prop-desc">Control randomness (default: 0.7)</div>
               </div>
               <div className="property-row-detailed">
                  <div className="prop-meta">
                    <span className="name">max_tokens</span>
                    <span className="type">integer</span>
                  </div>
                  <div className="prop-desc">Max generation limit (default: 1024)</div>
               </div>
            </div>

            <div className="code-block-modern">
               <div className="code-block-header">
                  <div className="code-lang"><Terminal size={14} /> cURL Example</div>
                  <button 
                    className="copy-btn-modern" 
                    onClick={() => handleCopy('curl -X POST http://<gateway-ip>/api/ai/models/tinyllama/generate -H "X-API-KEY: ak_..." -H "Content-Type: application/json" -d \'{"messages": [{"role": "user", "content": "Explain RAG in one sentence."}], "temperature": 0.5}\'', 'c2')}
                  >
                    {copiedId === 'c2' ? <><Check size={14} /> Copied</> : <><Copy size={14} /> Copy Code</>}
                  </button>
               </div>
               <pre><code>{`curl -X POST http://<gateway-ip>/api/ai/models/tinyllama/generate \\
     -H "X-API-KEY: ak_..." \\
     -H "Content-Type: application/json" \\
     -d '{
       "messages": [{"role": "user", "content": "Explain RAG in one sentence."}],
       "temperature": 0.5
     }'`}</code></pre>
            </div>
          </section>

          <section id="embed" className="docs-section">
            <h2>3. Semantic Search (Embeddings)</h2>
            <p>
              Generate vector embeddings for RAG pipelines. Only dedicated embedding models 
              (e.g., <code>nomic-embed-text</code>) are allowed.
            </p>
            <div className="endpoint-pill">
              <span className="method post">POST</span>
              <code className="path">/api/ai/models/&lt;model_id&gt;/embed</code>
            </div>

            <div className="property-grid">
               <div className="property-header">
                  <span className="label">Request Body</span>
               </div>
               <div className="property-row-detailed">
                  <div className="prop-meta">
                    <span className="name">input</span>
                    <span className="type">string | array</span>
                    <span className="req">Required</span>
                  </div>
                  <div className="prop-desc">Text or list of strings to be vectorized</div>
               </div>
            </div>

            <div className="code-block-modern">
               <div className="code-block-header">
                  <div className="code-lang"><Terminal size={14} /> cURL Example</div>
                  <button 
                    className="copy-btn-modern" 
                    onClick={() => handleCopy('curl -X POST http://<gateway-ip>/api/ai/models/nomic-embed-text/embed -H "X-API-KEY: ak_..." -H "Content-Type: application/json" -d \'{"input": "This is a document about machine learning."}\'', 'c3')}
                  >
                    {copiedId === 'c3' ? <><Check size={14} /> Copied</> : <><Copy size={14} /> Copy Code</>}
                  </button>
               </div>
               <pre><code>{`curl -X POST http://<gateway-ip>/api/ai/models/nomic-embed-text/embed \\
     -H "X-API-KEY: ak_..." \\
     -H "Content-Type: application/json" \\
     -d '{
       "input": "This is a document about machine learning."
     }'`}</code></pre>
            </div>
          </section>

          <hr className="docs-divider" />

          <section id="rejections" className="docs-section">
            <h2>Security & Role Enforcement</h2>
            <p>
              The Darkny Gateway enforces strict model roles. Attempting to use an embedding model 
              for text generation (or vice versa) results in an immediate rejection.
            </p>

            <div className="error-grid">
               <div className="error-card">
                  <div className="error-header">
                    <span className="error-code">400 Bad Request</span>
                    <span className="error-type">ModelRoleMismatch</span>
                  </div>
                  <div className="error-body">
                    The requested operation is inconsistent with the model's architectural role. 
                    Generative models cannot embed, and embedding models cannot generate.
                  </div>
               </div>
            </div>
          </section>

          <section id="errors" className="docs-section">
            <h2>Error Codes</h2>
            <p>Common response codes returned by the AI orchestration layer.</p>
            <div className="docs-table-wrapper">
              <table className="docs-table-v2">
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Type</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><code>401</code></td>
                    <td><code>Unauthorized</code></td>
                    <td>Missing or invalid X-API-KEY header</td>
                  </tr>
                  <tr>
                    <td><code>403</code></td>
                    <td><code>Forbidden</code></td>
                    <td>Key has been revoked or has insufficient permissions</td>
                  </tr>
                  <tr>
                    <td><code>429</code></td>
                    <td><code>TooManyRequests</code></td>
                    <td>Rate limit exceeded for the provided API key</td>
                  </tr>
                  <tr>
                    <td><code>503</code></td>
                    <td><code>ServiceUnavailable</code></td>
                    <td>Underlying AI engine (Ollama/vLLM) is restarting or overloaded</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>

        <footer className="docs-footer-modern">
          <p>© 2026 Darkny AI Orchestration Infrastructure. Stable API v1.2.0.</p>
        </footer>
      </main>
    </div>
  );
};

export default Documentation;
