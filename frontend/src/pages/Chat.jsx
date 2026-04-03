import React, { useState, useEffect, useRef, useCallback } from 'react';
import { chatApi, ENDPOINTS } from '../lib/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import {
  Plus, Send, Trash2, MessageSquare, Bot, User, Loader2,
  ChevronLeft, MoreVertical, Pencil, Check, X, Zap, Brain,
  Pin, PinOff, AlertCircle, StopCircle, Copy, CheckCheck,
  Sparkles, Command, Shield, ArrowUp, RefreshCcw
} from 'lucide-react';
import { useParams, useNavigate } from 'react-router-dom';
import './Chat.css';


// ── Constants ─────────────────────────────────────────────────────────────────
const GATEWAY    = import.meta.env.VITE_API_GATEWAY || 'http://localhost:80';
const CHAT_BASE  = `${GATEWAY}/api/chat`;

function formatTime(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  const today = new Date();
  if (d.toDateString() === today.toDateString()) return 'Today';
  const yest = new Date(today); yest.setDate(today.getDate() - 1);
  if (d.toDateString() === yest.toDateString()) return 'Yesterday';
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

function getToken() { return localStorage.getItem('access_token'); }

// ── Stream helper ─────────────────────────────────────────────────────────────
async function* streamSSE(url, body, signal) {
  const resp = await fetch(url, {
    method:  'POST',
    signal:  signal,
    headers: {
      'Content-Type':  'application/json',
      'Authorization': `Bearer ${getToken()}`,
    },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.message || `HTTP ${resp.status}`);
  }
  const reader  = resp.body.getReader();
  const decoder = new TextDecoder();
  let   buffer  = '';
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop();
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6).trim();
        if (data === '[DONE]') return;
        try { yield JSON.parse(data); } catch { /* skip */ }
      }
    }
  }
}


// ── Copy button ───────────────────────────────────────────────────────────────
function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button className="code-copy-btn-v2" onClick={copy} title="Copy code">
      {copied ? <CheckCheck size={14} /> : <Copy size={14} />}
      <span>{copied ? 'Copied' : 'Copy'}</span>
    </button>
  );
}

// ── Markdown Components ───────────────────────────────────────────────────────
const MD_COMPONENTS = {
  code({ node, inline, className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '');
    const codeText = String(children).replace(/\n$/, '');
    
    if (inline) {
      return <code className="modern-inline-code" {...props}>{children}</code>;
    }

    // High-performance block rendering (with or without language)
    return (
      <div className="modern-code-block">
        <div className="code-header-v2">
          <div className="header-meta">
            <span className="lang-dot"></span>
            <span className="lang-name">{match ? match[1] : 'Plain Text'}</span>
          </div>
          <CopyButton text={codeText} />
        </div>
        <div className="code-content-v2">
          <code className={className} {...props}>{children}</code>
        </div>
      </div>
    );
  },

  a({ href, children }) {
    return <a href={href} target="_blank" rel="noopener noreferrer" className="modern-link">{children}</a>;
  },
  table({ children }) { 
    return <div className="modern-table-container"><table className="modern-table">{children}</table></div>; 
  },
};

// ── Message Bubble ────────────────────────────────────────────────────────────
function MessageBubble({ msg, onPin }) {
  if (msg.role === 'system') {
    return (
      <div className="system-banner-v2">
         <Shield size={14} /> <span>{msg.content}</span>
      </div>
    );
  }
  const isUser = msg.role === 'user';
  return (
    <div className={`message-row-v2 ${isUser ? 'user' : 'assistant'}`}>
      <div className="avatar-v2">
        {isUser ? <User size={16} strokeWidth={2.5} /> : <Sparkles size={16} strokeWidth={2.5} />}
      </div>
      <div className="bubble-canvas-v2">
        <div className={`bubble-v2 ${isUser ? 'user' : 'assistant'} ${msg._streaming ? 'streaming' : ''}`}>
          {isUser ? (
            <div className="user-content-v2">{msg.content}</div>
          ) : (
            <div className="assistant-content-v2 markdown-body-v2">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
                components={MD_COMPONENTS}
              >
                {msg.content}
              </ReactMarkdown>
              {msg._streaming && <span className="streaming-dot"></span>}
            </div>

          )}
        </div>
        
        {!msg._streaming && (
          <div className="bubble-actions-v2">
            <div className="time-meta-v2">{formatTime(msg.created_at)}</div>
            <div className="action-set">
               {onPin && (
                 <button className="bubble-tool-btn" onClick={() => onPin(msg.id)}>
                   {msg.is_pinned ? <PinOff size={14} /> : <Pin size={14} />}
                 </button>
               )}
               {!isUser && <button className="bubble-tool-btn"><Copy size={14} /></button>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Session Item ──────────────────────────────────────────────────────────────
function SessionItem({ session, active, onClick, onDelete, onRename }) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle]     = useState(session.title);

  useEffect(() => { setTitle(session.title); }, [session.title]);

  const save = async () => {
    const t = title.trim();
    if (t && t !== session.title) await onRename(session.id, t);
    setEditing(false);
  };

  return (
    <div className={`session-card-v2 ${active ? 'active' : ''}`} onClick={() => !editing && onClick(session)}>
      <div className="session-brand-icon">
        <MessageSquare size={16} />
      </div>
      <div className="session-title-wrap">
        {editing ? (
          <input
            className="session-edit-input-v2"
            value={title}
            onChange={e => setTitle(e.target.value)}
            onKeyDown={e => { 
              if (e.key === 'Enter') save(); 
              if (e.key === 'Escape') { setEditing(false); setTitle(session.title); } 
            }}
            onBlur={save}
            onClick={e => e.stopPropagation()}
            autoFocus
          />
        ) : (
          <span className="session-title-text">{session.title}</span>
        )}

      </div>
      <div className="session-action-group" onClick={e => e.stopPropagation()}>
         <button className="session-tool-mini" onClick={() => setEditing(!editing)}>
            <Pencil size={12} />
         </button>
         <button className="session-tool-mini danger" onClick={() => onDelete(session.id)}>
            <Trash2 size={12} />
         </button>
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────
const DRAFT_SESSION = { id: null, title: 'Identity Initialization' };

export default function Chat({ user }) {
  const { sessionId: urlSessionId } = useParams();
  const navigate = useNavigate();

  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [availableModels, setAvailableModels] = useState([]);
  const [input, setInput] = useState('');
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [sending, setSending] = useState(false);
  const [model, setModel] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [error, setError] = useState('');
  
  const abortRef = useRef(null);
  const messagesEnd = useRef(null);
  const textareaRef = useRef(null);

  // ── REHYDRATION LOGIC ──
  useEffect(() => {
    if (sessions.length > 0 && urlSessionId && urlSessionId !== 'new') {
      const found = sessions.find(s => String(s.id) === String(urlSessionId));
      if (found && activeSession?.id !== found.id) {
        openSession(found);
      }
    } else if (urlSessionId === 'new' && activeSession?.id !== null) {
      enterDraftMode();
    }
  }, [urlSessionId, sessions]);

  useEffect(() => { messagesEnd.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) { ta.style.height = 'auto'; ta.style.height = `${Math.min(ta.scrollHeight, 220)}px`; }
  }, [input]);

  useEffect(() => { 
    fetchSessions(); 
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const res = await chatApi.get(ENDPOINTS.CHAT_MODELS);
      const modelsList = res.data?.data?.models || res.data?.models || res.data?.data;
      if (Array.isArray(modelsList)) {
        const mapped = modelsList.map(m => {
          const id = m.name ? m.name.replace('models/', '') : m.id;
          const dn = m.displayName || id;
          const parts = dn.split(' - ');
          return { id, label: parts[0].trim(), desc: parts.length > 1 ? parts.slice(1).join(' - ').trim() : '' };
        });
        setAvailableModels(mapped);
        if (mapped.length > 0 && !model) setModel(mapped[0].id);
      }
    } catch (err) { console.error('Failed to load models:', err); }
  };

  const fetchSessions = async () => {
    try {
      setLoadingSessions(true);
      const res = await chatApi.get('/sessions');
      const sessionList = res.data.data || [];
      setSessions(sessionList);
    } catch { setError('Could not load sessions'); }
    finally { setLoadingSessions(false); }
  };

  const openSession = useCallback(async (session) => {
    if (session.id === null) { 
      setActiveSession(DRAFT_SESSION); 
      setMessages([]); 
      navigate('/chat/new');
      return; 
    }
    setActiveSession(session);
    if (session.id !== urlSessionId) navigate(`/chat/${session.id}`);
    setModel(session.model || (availableModels.length > 0 ? availableModels[0].id : ''));
    try {
      const res = await chatApi.get(`/sessions/${session.id}/messages`);
      setMessages(res.data.data || []);
    } catch { setMessages([]); }
  }, [availableModels, urlSessionId, navigate]);

  const enterDraftMode = () => {
    setActiveSession(DRAFT_SESSION);
    setMessages([]);
    setError('');
    if (urlSessionId !== 'new') navigate('/chat/new');
    if (availableModels.length > 0) setModel(availableModels[0].id);
  };


  const deleteSession = async (id) => {
    if (!window.confirm("Archive this conversation?")) return;
    await chatApi.delete(`/sessions/${id}`);
    setSessions(prev => prev.filter(s => s.id !== id));
    if (activeSession?.id === id) { setActiveSession(null); setMessages([]); }
  };

  const renameSession = async (id, title) => {
    await chatApi.patch(`/sessions/${id}`, { title });
    setSessions(prev => prev.map(s => s.id === id ? { ...s, title } : s));
  };

  const sendMessage = async () => {
    if (!input.trim() || sending || !activeSession) return;
    const content = input.trim();
    setInput('');
    setSending(true);
    setError('');

    const tempId = `temp-${Date.now()}`;
    setMessages(prev => [...prev, { id: tempId, role: 'user', content, created_at: new Date().toISOString() }]);

    const aiBubbleId = `ai-${Date.now()}`;
    setMessages(prev => [...prev, { id: aiBubbleId, role: 'assistant', content: '', created_at: new Date().toISOString(), _streaming: true }]);

    const isDraft = activeSession.id === null;
    const url = isDraft ? `${CHAT_BASE}/quick-stream` : `${CHAT_BASE}/sessions/${activeSession.id}/stream`;
    abortRef.current = new AbortController();

    try {
      let sessionId = activeSession.id;
      let prevContent = '';
      for await (const event of streamSSE(url, { content, model, temperature: 0.7, max_tokens: 2048, use_context: true }, abortRef.current?.signal)) {
        if (event.type === 'session') {
          sessionId = event.session_id;
          setActiveSession(s => ({ ...s, id: sessionId, title: event.title || s.title }));
        }
        if (event.type === 'token') {
          prevContent += event.text;
          setMessages(prev => prev.map(m => m.id === aiBubbleId ? { ...m, content: prevContent } : m));
        }
        if (event.type === 'done') {
          setMessages(prev => prev.map(m => m.id === aiBubbleId ? { ...m, ...event.assistant_message, _streaming: false } : m));
          if (isDraft) fetchSessions();
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') {
        setError(e.message || 'Transmission unstable');
        setMessages(prev => prev.filter(m => m.id !== aiBubbleId));
      }
    } finally {
      setSending(false);
      abortRef.current = null;
    }
  };

  const stopStream = () => {
    abortRef.current?.abort();
    setSending(false);
    setMessages(prev => prev.map(m => m._streaming ? { ...m, _streaming: false } : m));
  };

  return (
    <div className="chat-container-v2">
      
      {/* ── HIGH-END SIDEBAR ── */}
      <aside className={`modern-sidebar-v2 ${sidebarOpen ? 'open' : 'closed'}`}>
         <div className="sidebar-top-v2">
            <button className="new-intel-btn" onClick={enterDraftMode}>
               <Plus size={18} />
               <span>Initial New Intel</span>
            </button>
         </div>

         <div className="sidebar-middle-v2">
            <div className="sidebar-group-label">Memory Core</div>
            <div className="history-list-v2">
               {loadingSessions ? (
                 <div className="history-loader"><Loader2 className="animate-spin" /></div>
               ) : sessions.map(s => (
                 <SessionItem 
                   key={s.id} 
                   session={s} 
                   active={activeSession?.id === s.id}
                   onClick={openSession}
                   onDelete={deleteSession}
                   onRename={renameSession}
                 />
               ))}
            </div>
         </div>

         <div className="sidebar-bottom-v2">
            <div className="model-selector-v2">
               <label><Zap size={12} /> DEFAULT ENGINE</label>
               <select value={model} onChange={e => setModel(e.target.value)}>
                  {availableModels.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
               </select>
            </div>
         </div>
         
         <button className="sidebar-collapse-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
            <ChevronLeft size={16} />
         </button>
      </aside>

      {/* ── CHAT ENGINE ── */}
      <main className="chat-engine-v2">
        {activeSession ? (
          <>
            {/* IMMERSIVE HEADER */}
            <header className="chat-header-v2">
               <div className="header-intel-v2">
                  <div className="intel-badge"><Bot size={16} /></div>
                  <div className="intel-info">
                     <h3>{activeSession.title}</h3>
                     <p>{availableModels.find(m => m.id === model)?.label} · Identity Verified</p>
                  </div>
               </div>
               <div className="header-tools-v2">
                  <button className="tool-btn-v2" onClick={enterDraftMode}><Plus size={20} /></button>
                  <button className="tool-btn-v2" onClick={fetchSessions}><RefreshCcw size={18} /></button>
               </div>
            </header>

            {/* MESSAGE CANVAS */}
            <div className="message-canvas-v2 scroll-y-auto">
               <div className="canvas-content-v2">
                  {messages.length === 0 ? (
                    <div className="empty-canvas-v2">
                       <Sparkles size={48} className="sparkle-icon" />
                       <h2>How can I assist your objectives today?</h2>
                       <p>Secure, context-aware AI orchestration fueled by Darkny Core.</p>
                       <div className="suggestion-grid">
                          <button onClick={() => setInput("Initialize security audit report")}>Execute Audit</button>
                          <button onClick={() => setInput("Optimize neural network parameters")}>Neural Optz</button>
                       </div>
                    </div>
                  ) : (
                    messages.map(m => <MessageBubble key={m.id} msg={m} />)
                  )}
                  <div ref={messagesEnd} />
               </div>
            </div>

            {/* INTERACTION ZONE */}
            <div className="interaction-zone-v2">
               <div className="interaction-wrap-v2">
                  <div className="interaction-box-v2">
                     <textarea
                        ref={textareaRef}
                        className="interaction-textarea-v2"
                        placeholder="Message Darkny AI..."
                        rows={1}
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }}}
                        disabled={sending}
                     />
                     <div className="interaction-tools-v2">
                        {sending ? (
                          <button className="exec-btn stop" onClick={stopStream}><StopCircle size={20} /></button>
                        ) : (
                          <button 
                            className={`exec-btn ${!input.trim() ? 'inactive' : 'active'}`} 
                            onClick={sendMessage}
                            disabled={!input.trim()}
                          >
                            <ArrowUp size={20} strokeWidth={3} />
                          </button>
                        )}
                     </div>
                  </div>
                  <div className="interaction-footer-v2">
                     <Command size={12} /> <span>Press Enter to send / Shift + Enter for new line</span>
                  </div>
               </div>
            </div>
          </>
        ) : (
          <div className="welcome-gate-v2">
             <div className="gate-mesh"></div>
             <div className="gate-content">
                <div className="gate-logo">
                   <Brain size={64} />
                </div>
                <h1>Welcome to <span>Darkny</span> AI</h1>
                <p>Deploying high-performance neural nodes for your enterprise environment.</p>
                <div className="gate-engine-grid">
                  {availableModels.slice(0, 3).map(m => (
                    <button key={m.id} className={`engine-card-v2 ${model === m.id ? 'active' : ''}`} onClick={() => setModel(m.id)}>
                       <Zap size={18} />
                       <div className="ec-info">
                          <div className="ec-label">{m.label}</div>
                          <div className="ec-desc">{m.desc || 'Standard operative engine'}</div>
                       </div>
                    </button>
                  ))}
                </div>
                <button className="gate-init-btn" onClick={enterDraftMode}>
                  Initialize New Thread
                </button>
             </div>
          </div>
        )}
      </main>

      {error && (
        <div className="global-error-v2">
           <AlertCircle size={16} /> <span>{error}</span>
           <button onClick={() => setError('')}><X size={14} /></button>
        </div>
      )}

    </div>
  );
}
