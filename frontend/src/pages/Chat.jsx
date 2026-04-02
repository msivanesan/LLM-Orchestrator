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
} from 'lucide-react';
import './Chat.css';

// ── Constants ─────────────────────────────────────────────────────────────────
const GATEWAY    = import.meta.env.VITE_API_GATEWAY || 'http://localhost:80';
const CHAT_BASE  = `${GATEWAY}/api/chat`;

// Models will now be fetched dynamically from the backend

// ── Helpers ───────────────────────────────────────────────────────────────────
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

// ── Stream helper (fetch + ReadableStream) ────────────────────────────────────
async function* streamSSE(url, body) {
  const resp = await fetch(url, {
    method:  'POST',
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
    buffer = lines.pop();        // keep incomplete line
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6).trim();
        if (data === '[DONE]') return;
        try { yield JSON.parse(data); } catch { /* skip malformed */ }
      }
    }
  }
}

// ── Copy button for code blocks ───────────────────────────────────────────────
function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button className="code-copy-btn" onClick={copy} title="Copy code">
      {copied ? <CheckCheck size={13} /> : <Copy size={13} />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  );
}

// ── Markdown renderer components ──────────────────────────────────────────────
const MD_COMPONENTS = {
  // Code blocks with copy button
  code({ node, inline, className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '');
    const codeText = String(children).replace(/\n$/, '');
    if (!inline && match) {
      return (
        <div className="code-block">
          <div className="code-header">
            <span className="code-lang">{match[1]}</span>
            <CopyButton text={codeText} />
          </div>
          <code className={className} {...props}>{children}</code>
        </div>
      );
    }
    return <code className="inline-code" {...props}>{children}</code>;
  },
  // Open links in new tab
  a({ href, children }) {
    return <a href={href} target="_blank" rel="noopener noreferrer" className="md-link">{children}</a>;
  },
  // Tables
  table({ children }) { return <div className="md-table-wrap"><table className="md-table">{children}</table></div>; },
};

// ── Message bubble ────────────────────────────────────────────────────────────
function MessageBubble({ msg, onPin }) {
  if (msg.role === 'system') {
    return (
      <div className="chat-msg-system">
        <AlertCircle size={13} /> {msg.content}
      </div>
    );
  }
  const isUser = msg.role === 'user';
  return (
    <div className={`chat-msg-row ${isUser ? 'user' : 'assistant'}`}>
      <div className="chat-avatar">
        {isUser ? <User size={14} /> : <Bot size={14} />}
      </div>
      <div className="chat-bubble-wrap">
        <div className={`chat-bubble ${isUser ? 'user' : 'assistant'} ${msg.is_pinned ? 'pinned' : ''} ${msg._streaming ? 'streaming' : ''}`}>

          {isUser ? (
            /* User messages: plain text, preserve newlines */
            <pre className="chat-text">{msg.content}</pre>
          ) : (
            /* Assistant messages: full markdown rendering */
            <div className="chat-md">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
                components={MD_COMPONENTS}
              >
                {msg.content + (msg._streaming ? '▋' : '')}
              </ReactMarkdown>
            </div>
          )}

          {!msg._streaming && (
            <div className="chat-meta">
              <span>{formatTime(msg.created_at)}</span>
              {msg.tokens > 0 && <span>~{msg.tokens} tk</span>}
              {onPin && (
                <button className="pin-btn" onClick={() => onPin(msg.id)}
                  title={msg.is_pinned ? 'Unpin' : 'Pin'}>
                  {msg.is_pinned ? <PinOff size={11} /> : <Pin size={11} />}
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Typing indicator ──────────────────────────────────────────────────────────
function TypingIndicator() {
  return (
    <div className="chat-msg-row assistant">
      <div className="chat-avatar"><Bot size={14} /></div>
      <div className="chat-bubble assistant typing-bubble">
        <span className="dot" /><span className="dot" /><span className="dot" />
      </div>
    </div>
  );
}

// ── Session list item ─────────────────────────────────────────────────────────
function SessionItem({ session, active, onClick, onDelete, onRename }) {
  const [menu, setMenu]       = useState(false);
  const [editing, setEditing] = useState(false);
  const [title, setTitle]     = useState(session.title);
  const menuRef = useRef(null);

  // Sync title when session prop changes (auto-title update)
  useEffect(() => { setTitle(session.title); }, [session.title]);

  useEffect(() => {
    const close = (e) => { if (menuRef.current && !menuRef.current.contains(e.target)) setMenu(false); };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, []);

  const save = async () => {
    const t = title.trim();
    if (t && t !== session.title) await onRename(session.id, t);
    setEditing(false);
  };

  return (
    <div className={`session-item ${active ? 'active' : ''}`} onClick={() => !editing && onClick(session)}>
      <div className="session-icon"><MessageSquare size={15} /></div>
      <div className="session-info">
        {editing ? (
          <input
            className="session-rename-input"
            value={title}
            onChange={e => setTitle(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') save(); if (e.key === 'Escape') setEditing(false); }}
            onClick={e => e.stopPropagation()}
            autoFocus
          />
        ) : (
          <>
            <span className="session-title">{session.title}</span>
            <span className="session-date">{formatDate(session.updated_at)}</span>
          </>
        )}
      </div>
      <div className="session-actions" onClick={e => e.stopPropagation()} ref={menuRef}>
        {editing ? (
          <>
            <button className="icon-btn-sm" onClick={save}><Check size={13} /></button>
            <button className="icon-btn-sm" onClick={() => setEditing(false)}><X size={13} /></button>
          </>
        ) : (
          <>
            <button className="icon-btn-sm" onClick={() => setMenu(m => !m)}>
              <MoreVertical size={14} />
            </button>
            {menu && (
              <div className="session-menu">
                <button onClick={() => { setEditing(true); setMenu(false); }}>
                  <Pencil size={13} /> Rename
                </button>
                <button className="danger" onClick={() => { onDelete(session.id); setMenu(false); }}>
                  <Trash2 size={13} /> Delete
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ── Main Chat Page ────────────────────────────────────────────────────────────
const DRAFT_SESSION = { id: null, title: 'New Chat' };

export default function Chat({ user }) {
  const [sessions,      setSessions]      = useState([]);
  const [activeSession, setActiveSession] = useState(null); // null = welcome, DRAFT_SESSION = draft
  const [messages,      setMessages]      = useState([]);
  const [availableModels, setAvailableModels] = useState([]);
  const [input,         setInput]         = useState('');
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [sending,       setSending]       = useState(false);
  const [model,         setModel]         = useState('');
  const [sidebarOpen,   setSidebarOpen]   = useState(true);
  const [error,         setError]         = useState('');
  const abortRef    = useRef(null);   // AbortController for stopping stream
  const messagesEnd = useRef(null);
  const textareaRef = useRef(null);

  // Scroll to bottom on new messages
  useEffect(() => { messagesEnd.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) { ta.style.height = 'auto'; ta.style.height = `${Math.min(ta.scrollHeight, 180)}px`; }
  }, [input]);

  // Load sessions and models
  useEffect(() => { 
    fetchSessions(); 
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const res = await chatApi.get(ENDPOINTS.CHAT_MODELS);
      console.log("FETCH MODELS RESP:", res);
      const modelsList = res.data?.data?.models || res.data?.models || res.data?.data;
      if (Array.isArray(modelsList)) {
        console.log("MAPPED MODELS LIST:", modelsList);
        const mapped = modelsList.map(m => {
          const id = m.name ? m.name.replace('models/', '') : m.id;
          const dn = m.displayName || id;
          const parts = dn.split(' - ');
          return { id, label: parts[0].trim(), desc: parts.length > 1 ? parts.slice(1).join(' - ').trim() : '' };
        });
        console.log("FINAL MAPPED:", mapped);
        setAvailableModels(mapped);
        if (mapped.length > 0) setModel(mapped[0].id);
      }
    } catch (err) {
      console.error('Failed to load models:', err);
    }
  };

  const fetchSessions = async () => {
    try {
      setLoadingSessions(true);
      const res = await chatApi.get('/sessions');
      setSessions(res.data.data || []);
    } catch { setError('Could not load sessions'); }
    finally  { setLoadingSessions(false); }
  };

  const openSession = useCallback(async (session) => {
    if (session.id === null) { setActiveSession(DRAFT_SESSION); setMessages([]); return; }
    setActiveSession(session);
    setModel(session.model || (availableModels.length > 0 ? availableModels[0].id : ''));
    setError('');
    try {
      const res = await chatApi.get(`/sessions/${session.id}/messages`);
      setMessages(res.data.data || []);
    } catch { setMessages([]); }
  }, []);

  // Enter draft mode (no session created yet)
  const enterDraftMode = () => {
    setActiveSession(DRAFT_SESSION);
    setMessages([]);
    setError('');
    if (availableModels.length > 0) setModel(availableModels[0].id);
  };

  const deleteSession = async (id) => {
    await chatApi.delete(`/sessions/${id}`);
    setSessions(prev => prev.filter(s => s.id !== id));
    if (activeSession?.id === id) { setActiveSession(null); setMessages([]); }
  };

  const renameSession = async (id, title) => {
    await chatApi.patch(`/sessions/${id}`, { title });
    setSessions(prev => prev.map(s => s.id === id ? { ...s, title } : s));
    if (activeSession?.id === id) setActiveSession(s => ({ ...s, title }));
  };

  const pinMessage = async (messageId) => {
    if (!activeSession?.id) return;
    await chatApi.patch(`/sessions/${activeSession.id}/messages/${messageId}/pin`);
    setMessages(prev => prev.map(m => m.id === messageId ? { ...m, is_pinned: !m.is_pinned } : m));
  };

  const clearMessages = async () => {
    if (!activeSession?.id || !window.confirm('Clear all messages?')) return;
    await chatApi.delete(`/sessions/${activeSession.id}/messages`);
    setMessages([]);
  };

  // ── SEND (handles both draft → creates session, and existing session) ────────
  const sendMessage = async () => {
    if (!input.trim() || sending || !activeSession) return;
    const content = input.trim();
    setInput('');
    setSending(true);
    setError('');

    // Optimistic user bubble (no id yet in draft)
    const tempId   = `temp-${Date.now()}`;
    const userBubble = { id: tempId, role: 'user', content, created_at: new Date().toISOString(), tokens: 0, is_pinned: false };
    setMessages(prev => [...prev, userBubble]);

    // Streaming AI bubble
    const aiBubbleId = `ai-${Date.now()}`;
    setMessages(prev => [...prev, { id: aiBubbleId, role: 'assistant', content: '', created_at: new Date().toISOString(), tokens: 0, is_pinned: false, _streaming: true }]);

    const isDraft = activeSession.id === null;
    const url     = isDraft
      ? `${CHAT_BASE}/quick-stream`
      : `${CHAT_BASE}/sessions/${activeSession.id}/stream`;

    abortRef.current = new AbortController();

    try {
      let sessionId   = activeSession.id;
      let finalTitle  = activeSession.title;
      let prevContent = '';
      let finalUserMsg = null;
      let finalAiMsg  = null;

      for await (const event of streamSSE(url, { content, model, temperature: 0.7, max_tokens: 1024, use_context: true })) {
        if (event.type === 'session') {
          // New session was created
          sessionId  = event.session_id;
          finalTitle = event.title || 'New Chat';
          if (event.user_message) finalUserMsg = event.user_message;
          setActiveSession(s => ({ ...s, id: sessionId, title: finalTitle }));
        }

        if (event.type === 'token') {
          prevContent += event.text;
          setMessages(prev => prev.map(m =>
            m.id === aiBubbleId ? { ...m, content: prevContent } : m
          ));
        }

        if (event.type === 'done') {
          finalTitle   = event.title    || finalTitle;
          finalUserMsg = event.user_message  || finalUserMsg;
          finalAiMsg   = event.assistant_message;

          // Replace temp bubbles with real persisted messages
          setMessages(prev => [
            ...prev.filter(m => m.id !== tempId && m.id !== aiBubbleId),
            ...(finalUserMsg ? [finalUserMsg] : []),
            ...(finalAiMsg   ? [{ ...finalAiMsg, _streaming: false }] : []),
          ]);

          // Update sidebar
          if (isDraft && sessionId) {
            const newSession = { id: sessionId, title: finalTitle, model, updated_at: new Date().toISOString() };
            setSessions(prev => [newSession, ...prev]);
            setActiveSession(newSession);
          } else {
            setSessions(prev => prev.map(s =>
              s.id === sessionId ? { ...s, title: finalTitle, updated_at: new Date().toISOString() } : s
            ));
            setActiveSession(s => ({ ...s, title: finalTitle }));
          }
        }

        if (event.type === 'error') {
          setError(event.message || 'AI error');
          setMessages(prev => prev.filter(m => m.id !== aiBubbleId));
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') {
        setError(e.message || 'Connection error');
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
    setMessages(prev => prev.map(m =>
      m._streaming ? { ...m, _streaming: false } : m
    ));
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const isDraft = activeSession?.id === null;

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="chat-app">

      {/* ── Sidebar ── */}
      <aside className={`chat-sidebar ${sidebarOpen ? '' : 'collapsed'}`}>
        <div className="chat-sidebar-header">
          <div className="chat-brand"><Brain size={20} />{sidebarOpen && <span>Darkny chat</span>}</div>
          <button className="icon-btn-sm" onClick={() => setSidebarOpen(o => !o)}>
            <ChevronLeft size={18} style={{ transform: sidebarOpen ? '' : 'rotate(180deg)', transition: 'transform .25s' }} />
          </button>
        </div>

        {sidebarOpen && (
          <>
            <div className="sidebar-model-select">
              <label>Default Model</label>
              <select value={model} onChange={e => setModel(e.target.value)}>
                {availableModels.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
              </select>
            </div>

            <button id="new-chat-btn" className="new-chat-btn" onClick={enterDraftMode}>
              <Plus size={16} /> New Chat
            </button>

            <div className="session-list-label">Recent Chats</div>

            <div className="session-list">
              {/* Draft entry */}
              {isDraft && (
                <div className="session-item active">
                  <div className="session-icon"><MessageSquare size={15} /></div>
                  <div className="session-info">
                    <span className="session-title">New Chat</span>
                    <span className="session-date">Draft</span>
                  </div>
                </div>
              )}

              {loadingSessions ? (
                <div className="session-loading"><Loader2 size={16} className="animate-spin" /> Loading…</div>
              ) : sessions.length === 0 && !isDraft ? (
                <div className="session-empty">No chats yet. Start one!</div>
              ) : (
                sessions.map(s => (
                  <SessionItem key={s.id} session={s}
                    active={activeSession?.id === s.id}
                    onClick={openSession}
                    onDelete={deleteSession}
                    onRename={renameSession}
                  />
                ))
              )}
            </div>
          </>
        )}
      </aside>

      {/* ── Main area ── */}
      <div className="chat-main">
        {!activeSession ? (
          /* Welcome */
          <div className="chat-welcome">
            <div className="welcome-glow" />
            <div className="welcome-icon"><Bot size={48} /></div>
            <h1>Darkny Assistant</h1>
            <p>Your private, high-performance LLM companion.</p>
            <div className="welcome-model-grid">
              {availableModels.map(m => (
                <button key={m.id}
                  className={`welcome-model-card ${model === m.id ? 'selected' : ''}`}
                  onClick={() => setModel(m.id)}>
                  <Zap size={16} />
                  <span className="wmc-label">{m.label}</span>
                  <span className="wmc-desc">{m.desc}</span>
                </button>
              ))}
            </div>
            <button id="welcome-new-chat-btn" className="new-chat-btn large" onClick={enterDraftMode}>
              <Plus size={18} /> Start New Chat
            </button>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="chat-header">
              <div className="chat-header-left">
                <MessageSquare size={18} />
                <span className={isDraft ? 'title-draft' : ''}>{activeSession.title}</span>
                {isDraft && <span className="draft-badge">Draft</span>}
              </div>
              <div className="chat-header-right">
                <select id="model-switcher" className="model-switcher" value={model}
                  onChange={async (e) => {
                    const m = e.target.value;
                    setModel(m);
                    if (activeSession.id) {
                      await chatApi.patch(`/sessions/${activeSession.id}`, { model: m });
                    }
                  }}>
                  {availableModels.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
                </select>
                {activeSession.id && (
                  <button id="clear-msgs-btn" className="icon-btn-sm danger" onClick={clearMessages} title="Clear messages">
                    <Trash2 size={15} />
                  </button>
                )}
              </div>
            </div>

            {error && (
              <div className="chat-error-banner">
                <AlertCircle size={15} /> {error}
                <button onClick={() => setError('')}><X size={14} /></button>
              </div>
            )}

            {/* Messages */}
            <div className="chat-messages">
              {messages.length === 0 && (
                <div className="chat-empty-state">
                  <Bot size={32} />
                  <p>{isDraft ? "Type your first message to start the conversation" : "No messages yet"}</p>
                </div>
              )}
              {messages.map(msg => (
                <MessageBubble key={msg.id} msg={msg} onPin={activeSession.id ? pinMessage : null} />
              ))}
              <div ref={messagesEnd} />
            </div>

            {/* Input */}
            <div className="chat-input-area">
              <div className="chat-input-box">
                <textarea id="chat-input" ref={textareaRef} className="chat-textarea"
                  rows={1} disabled={sending}
                  placeholder={isDraft ? "Type your first message — a session will be created automatically…" : "Message the AI… (Enter to send)"}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKey}
                />
                {sending ? (
                  <button id="stop-btn" className="send-btn stop" onClick={stopStream} title="Stop">
                    <StopCircle size={18} />
                  </button>
                ) : (
                  <button id="send-btn"
                    className={`send-btn ${!input.trim() ? 'disabled' : ''}`}
                    onClick={sendMessage} disabled={!input.trim()}>
                    <Send size={18} />
                  </button>
                )}
              </div>
              <div className="chat-input-hint">
                {isDraft
                  ? <>Session will be created & named automatically on send · Model: <strong>{availableModels.find(m => m.id === model)?.label}</strong></>
                  : <>Model: <strong>{availableModels.find(m => m.id === model)?.label}</strong> · Context-aware · Streaming</>
                }
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
