import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Key, Cpu, Zap, Database, ShieldX, ChevronRight,
  Copy, Check, BookOpen, ArrowRight, Terminal, Lock
} from 'lucide-react';
import './Docs.css';

const BASE_URL = 'http://<gateway-ip>';
const API_KEY_PLACEHOLDER = 'ak_your_key_here';

const CodeBlock = ({ code, language = 'bash' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="docs-code-block">
      <div className="docs-code-header">
        <span className="docs-code-lang">{language}</span>
        <button className="docs-copy-btn" onClick={handleCopy}>
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <pre><code>{code}</code></pre>
    </div>
  );
};

const ParamRow = ({ name, type, required, description }) => (
  <tr className="docs-param-row">
    <td>
      <code className="docs-param-name">{name}</code>
      {required && <span className="docs-badge required">required</span>}
      {!required && <span className="docs-badge optional">optional</span>}
    </td>
    <td><span className="docs-param-type">{type}</span></td>
    <td className="docs-param-desc">{description}</td>
  </tr>
);

const sections = [
  { id: 'authentication', label: 'Authentication', icon: Lock },
  { id: 'models', label: 'Model Discovery', icon: Database },
  { id: 'generate', label: 'Text Generation', icon: Zap },
  { id: 'embed', label: 'Embeddings', icon: Cpu },
  { id: 'errors', label: 'Error Handling', icon: ShieldX },
];

export default function Docs() {
  const [activeSection, setActiveSection] = useState('authentication');

  const scrollTo = (id) => {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className="docs-page">
      {/* Top Bar */}
      <header className="docs-topbar">
        <div className="docs-topbar-brand">
          <BookOpen size={20} />
          <span>AI Gateway Docs</span>
        </div>
        <Link to="/login" className="docs-topbar-login">
          Sign In <ArrowRight size={14} />
        </Link>
      </header>

      <div className="docs-layout">
        {/* Sidebar Nav */}
        <aside className="docs-sidebar">
          <p className="docs-sidebar-label">Getting Started</p>
          <nav className="docs-sidebar-nav">
            {sections.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                className={`docs-nav-item ${activeSection === id ? 'active' : ''}`}
                onClick={() => scrollTo(id)}
              >
                <Icon size={16} />
                {label}
                {activeSection === id && <ChevronRight size={14} className="docs-nav-chevron" />}
              </button>
            ))}
          </nav>
          <div className="docs-sidebar-callout">
            <Key size={16} />
            <div>
              <strong>Need an API Key?</strong>
              <p>Contact your admin to generate a key from the dashboard.</p>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="docs-content">

          {/* Hero */}
          <div className="docs-hero">
            <div className="docs-hero-badge">v1.0 — Production Ready</div>
            <h1>AI Gateway API Reference</h1>
            <p>
              A unified, authenticated endpoint for text generation and semantic embeddings.
              Strict model-role enforcement ensures generative and embedding workloads never mix.
            </p>
          </div>

          {/* ── Authentication ── */}
          <section id="authentication" className="docs-section">
            <div className="docs-section-header">
              <Lock size={20} className="docs-section-icon" />
              <h2>Authentication</h2>
            </div>
            <p>Every request must include your API key in the <code>X-API-KEY</code> header. Bearer tokens are not supported.</p>
            <div className="docs-callout warn">
              <ShieldX size={16} />
              Do <strong>not</strong> expose your API key in client-side code or public repositories.
            </div>
            <CodeBlock language="http" code={`X-API-KEY: ${API_KEY_PLACEHOLDER}\nContent-Type: application/json`} />
          </section>

          {/* ── Model Discovery ── */}
          <section id="models" className="docs-section">
            <div className="docs-section-header">
              <Database size={20} className="docs-section-icon" />
              <h2>Model Discovery</h2>
            </div>
            <p>Retrieve all available models and their assigned roles. The list is cached for <strong>12 hours</strong> on the server for performance.</p>
            <div className="docs-endpoint-tag">
              <span className="docs-method get">GET</span>
              <code>/api/ai/models</code>
            </div>
            <CodeBlock code={`curl -X GET ${BASE_URL}/api/ai/models \\\n     -H "X-API-KEY: ${API_KEY_PLACEHOLDER}"`} />
            <h4>Example Response</h4>
            <CodeBlock language="json" code={`{\n  "models": [\n    { "id": "tinyllama", "role": "generative" },\n    { "id": "nomic-embed-text", "role": "embedding" }\n  ]\n}`} />
          </section>

          {/* ── Text Generation ── */}
          <section id="generate" className="docs-section">
            <div className="docs-section-header">
              <Zap size={20} className="docs-section-icon" />
              <h2>Text Generation</h2>
            </div>
            <p>Generate text using a chat/generative model. Only models with the <strong>generative</strong> role are allowed on this endpoint.</p>
            <div className="docs-endpoint-tag">
              <span className="docs-method post">POST</span>
              <code>/api/ai/models/<span className="docs-path-param">{'{model_id}'}</span>/generate</code>
            </div>

            <h4>Request Parameters</h4>
            <table className="docs-param-table">
              <thead>
                <tr>
                  <th>Parameter</th><th>Type</th><th>Description</th>
                </tr>
              </thead>
              <tbody>
                <ParamRow name="messages" type="array" required description='List of message objects: {"role": "user", "content": "..."}' />
                <ParamRow name="temperature" type="float" description="Randomness of output. Defaults to 0.7." />
                <ParamRow name="max_tokens" type="integer" description="Maximum tokens to generate. Defaults to 1024." />
              </tbody>
            </table>

            <h4>Example Request</h4>
            <CodeBlock code={`curl -X POST ${BASE_URL}/api/ai/models/tinyllama/generate \\\n     -H "X-API-KEY: ${API_KEY_PLACEHOLDER}" \\\n     -H "Content-Type: application/json" \\\n     -d '{\n       "messages": [{"role": "user", "content": "Explain RAG in one sentence."}],\n       "temperature": 0.5\n     }'`} />

            <h4>Example Response</h4>
            <CodeBlock language="json" code={`{\n  "content": "RAG combines retrieval of relevant documents with generation...",\n  "model": "tinyllama",\n  "usage": { "prompt_tokens": 18, "completion_tokens": 42, "total_tokens": 60 }\n}`} />
          </section>

          {/* ── Embeddings ── */}
          <section id="embed" className="docs-section">
            <div className="docs-section-header">
              <Cpu size={20} className="docs-section-icon" />
              <h2>Embeddings (RAG)</h2>
            </div>
            <p>Generate vector embeddings for semantic search and RAG pipelines. Only models with the <strong>embedding</strong> role are allowed.</p>
            <div className="docs-endpoint-tag">
              <span className="docs-method post">POST</span>
              <code>/api/ai/models/<span className="docs-path-param">{'{model_id}'}</span>/embed</code>
            </div>

            <h4>Request Parameters</h4>
            <table className="docs-param-table">
              <thead>
                <tr>
                  <th>Parameter</th><th>Type</th><th>Description</th>
                </tr>
              </thead>
              <tbody>
                <ParamRow name="input" type="string / array" required description="The text (or list of texts) to embed into a vector." />
              </tbody>
            </table>

            <h4>Example Request</h4>
            <CodeBlock code={`curl -X POST ${BASE_URL}/api/ai/models/nomic-embed-text/embed \\\n     -H "X-API-KEY: ${API_KEY_PLACEHOLDER}" \\\n     -H "Content-Type: application/json" \\\n     -d '{\n       "input": "This is a document about machine learning."\n     }'`} />

            <h4>Example Response</h4>
            <CodeBlock language="json" code={`{\n  "embedding": [0.023, -0.114, 0.887, ...],\n  "model": "nomic-embed-text",\n  "usage": { "prompt_tokens": 9, "total_tokens": 9 }\n}`} />
          </section>

          {/* ── Errors ── */}
          <section id="errors" className="docs-section">
            <div className="docs-section-header">
              <ShieldX size={20} className="docs-section-icon" />
              <h2>Error Handling</h2>
            </div>
            <p>The gateway uses standard HTTP status codes and returns structured JSON errors.</p>

            <table className="docs-param-table">
              <thead>
                <tr><th>Status</th><th>Error Type</th><th>Cause</th></tr>
              </thead>
              <tbody>
                <tr>
                  <td><span className="docs-badge warn">401</span></td>
                  <td><code>Unauthorized</code></td>
                  <td>Missing or invalid <code>X-API-KEY</code> header.</td>
                </tr>
                <tr>
                  <td><span className="docs-badge required">400</span></td>
                  <td><code>ModelRoleMismatch</code></td>
                  <td>Using an embedding model on the generate endpoint (or vice versa).</td>
                </tr>
                <tr>
                  <td><span className="docs-badge required">404</span></td>
                  <td><code>ModelNotFound</code></td>
                  <td>The requested model does not exist in Ollama.</td>
                </tr>
                <tr>
                  <td><span className="docs-badge required">500</span></td>
                  <td><code>InternalError</code></td>
                  <td>Upstream Ollama failure or service unavailability.</td>
                </tr>
              </tbody>
            </table>

            <h4>Example Error Response</h4>
            <CodeBlock language="json" code={`{\n  "error": "Model 'nomic-embed-text' is a dedicated embedding model and cannot be used for text generation.",\n  "type": "ModelRoleMismatch"\n}`} />
          </section>

          <footer className="docs-footer">
            <Terminal size={14} />
            AI Gateway &mdash; Internal Platform
          </footer>
        </main>
      </div>
    </div>
  );
}
