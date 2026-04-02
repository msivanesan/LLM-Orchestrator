import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Book, Cpu, Key, Users, ArrowLeft, Terminal, Copy, AlertTriangle, Search, Zap, Sun, Moon } from 'lucide-react';

const Documentation = ({ theme, toggleTheme }) => {
  return (
    <div className="docs-container">
      {/* 📘 Documentation Sidebar */}
      <aside className="docs-sidebar">
        <div className="docs-logo">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <ShieldCheck color="#E11D48" size={24} />
              <span style={{ color: 'var(--text-main)', fontWeight: 800 }}>Darkny</span>
            </Link>
            <button className="theme-toggle-btn" onClick={toggleTheme} style={{ padding: '6px' }}>
              {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            </button>
          </div>
        </div>
        <div className="docs-menu">
          <div className="docs-menu-group">
            <span className="group-title">Getting Started</span>
            <a href="#introduction" className="active">Introduction</a>
            <a href="#auth">Authentication</a>
          </div>
          <div className="docs-menu-group">
            <span className="group-title">Endpoints</span>
            <a href="#models">Model Discovery</a>
            <a href="#generate">Text Generation</a>
            <a href="#embed">Semantic Search</a>
          </div>
          <div className="docs-menu-group">
            <span className="group-title">Security</span>
            <a href="#rejections">Role Enforcement</a>
            <a href="#errors">Error Codes</a>
          </div>
        </div>
      </aside>

      {/* 📄 Main Content Area */}
      <main className="docs-main">
        <header className="docs-header">
           <Link to="/" className="back-link"><ArrowLeft size={16} /> Back to Home</Link>
           <div className="docs-actions">
              <span className="version-pill">API v1.2.0-stable</span>
           </div>
        </header>

        <section id="introduction" className="docs-content">
          <div className="content-badge">Docs / Introduction</div>
          <h1>AI Gateway <span>Guidance</span></h1>
          <p className="lead">
            Welcome to the Darkny AI Gateway. This documentation provides technical guidance for 
            external agents and developers connecting to our high-performance model orchestration layer.
          </p>

          <h2 id="auth">Authentication</h2>
          <p>
            All requests to the Darkny Gateway must include your designated API key. Unlike traditional 
            APIs, the gateway uses a specific header for model-layer security.
          </p>

          <blockquote className="info-box" style={{ borderLeftColor: '#E11D48' }}>
             <AlertTriangle size={20} color="#E11D48" style={{ marginBottom: '0.5rem' }} />
             <strong>IMPORTANT:</strong> Do not use <code>Bearer</code> tokens. The gateway specifically 
             expects the <code>X-API-KEY</code> header for validation.
          </blockquote>

          <div className="property-grid">
             <div className="property-row header-row">
                <span className="prop-label">Required Headers</span>
             </div>
             <div className="property-row">
                <div className="prop-key">X-API-KEY</div>
                <div className="prop-val">ak_your_key_here</div>
                <button className="copy-btn-mini"><Copy size={12} /></button>
             </div>
             <div className="property-row">
                <div className="prop-key">Content-Type</div>
                <div className="prop-val">application/json</div>
                <button className="copy-btn-mini"><Copy size={12} /></button>
             </div>
          </div>

          <hr style={{ margin: '4rem 0', opacity: 0.1 }} />

          <h2 id="models">1. Model Discovery</h2>
          <p>
            Retrieve a live list of available models and their current capabilities (Generative vs. Embedding).
          </p>
          <div className="endpoint-tag">GET /api/ai/models</div>

          <div className="code-block">
             <div className="code-header">
                <span className="lang">cURL Request</span>
                <button className="copy-btn"><Copy size={14} /></button>
             </div>
             <pre>
<code>{`curl -X GET http://<gateway-ip>/api/ai/models \\
     -H "X-API-KEY: ak_..."`}</code>
             </pre>
          </div>

          <h2 id="generate">2. Generative AI (Text)</h2>
          <p>
            Use this endpoint for chat, reasoning, or content creation. Only generative models 
            (e.g., <code>llama3</code>, <code>tinyllama</code>) are permitted here.
          </p>
          <div className="endpoint-tag">POST /api/ai/models/&lt;model_id&gt;/generate</div>

          <div className="property-grid">
             <div className="property-row header-row">
                <span className="prop-label">Request Parameters</span>
             </div>
             <div className="property-row">
                <div className="prop-key">messages</div>
                <div className="prop-val-wrapper">
                  <div className="prop-val"><strong>Required</strong>. Array of message objects</div>
                  <button className="copy-btn-mini"><Copy size={12} /></button>
                </div>
             </div>
             <div className="property-row">
                <div className="prop-key">temperature</div>
                <div className="prop-val-wrapper">
                  <div className="prop-val">float. Control randomness (default: 0.7)</div>
                  <button className="copy-btn-mini"><Copy size={12} /></button>
                </div>
             </div>
             <div className="property-row">
                <div className="prop-key">max_tokens</div>
                <div className="prop-val-wrapper">
                  <div className="prop-val">integer. Max generation limit (default: 1024)</div>
                  <button className="copy-btn-mini"><Copy size={12} /></button>
                </div>
             </div>
          </div>

          <div className="code-block">
             <div className="code-header">
                <div className="dots"><span></span><span></span><span></span></div>
                <span className="lang">cURL Example</span>
                <button className="copy-btn"><Copy size={14} /></button>
             </div>
             <pre>
<code>{`curl -X POST http://<gateway-ip>/api/ai/models/tinyllama/generate \\
     -H "X-API-KEY: ak_..." \\
     -H "Content-Type: application/json" \\
     -d '{
       "messages": [{"role": "user", "content": "Explain RAG in one sentence."}],
       "temperature": 0.5
     }'`}</code>
             </pre>
          </div>

          <h2 id="embed">3. Semantic Search (Embeddings)</h2>
          <p>
            Generate vector embeddings for RAG pipelines. Only dedicated embedding models 
            (e.g., <code>nomic-embed-text</code>) are allowed.
          </p>
          <div className="endpoint-tag">POST /api/ai/models/&lt;model_id&gt;/embed</div>

          <div className="property-grid">
             <div className="property-row header-row">
                <span className="prop-label">Request Body</span>
             </div>
             <div className="property-row">
                <div className="prop-key">input</div>
                <div className="prop-val-wrapper">
                  <div className="prop-val"><strong>Required</strong>. String or Array of text to vectorize</div>
                  <button className="copy-btn-mini"><Copy size={12} /></button>
                </div>
             </div>
          </div>

          <div className="code-block">
             <div className="code-header">
                <div className="dots"><span></span><span></span><span></span></div>
                <span className="lang">cURL Example</span>
                <button className="copy-btn"><Copy size={14} /></button>
             </div>
             <pre>
<code>{`curl -X POST http://<gateway-ip>/api/ai/models/nomic-embed-text/embed \\
     -H "X-API-KEY: ak_..." \\
     -H "Content-Type: application/json" \\
     -d '{
       "input": "This is a document about machine learning."
     }'`}</code>
             </pre>
          </div>

          <h2 id="rejections">Security & Role Enforcement</h2>
          <p>
            The Darkny Gateway enforces strict model roles. Attempting to use an embedding model 
            for text generation (or vice versa) results in an immediate rejection.
          </p>

          <div className="property-grid">
             <div className="property-row header-row" style={{ borderLeft: '4px solid #EF4444' }}>
                <span className="prop-label" style={{ color: '#EF4444' }}>Error Response (400)</span>
             </div>
             <div className="property-row">
                <div className="prop-key">error</div>
                <div className="prop-val">Detailed mismatch description</div>
             </div>
             <div className="property-row">
                <div className="prop-key">type</div>
                <div className="prop-val" style={{ color: '#EF4444', fontWeight: 800 }}>ModelRoleMismatch</div>
             </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Documentation;
