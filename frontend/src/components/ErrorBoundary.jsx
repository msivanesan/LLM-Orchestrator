import React from 'react';
import { AlertCircle, RefreshCcw } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          gap: '1.5rem',
          background: 'var(--bg-color, #0f172a)',
          color: 'var(--text-main, #f8fafc)',
          fontFamily: "'Outfit', sans-serif",
          padding: '2rem',
          textAlign: 'center',
        }}>
          <div style={{
            width: 72, height: 72,
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 20,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#ef4444',
          }}>
            <AlertCircle size={36} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '0.5rem' }}>
              Something went wrong
            </h2>
            <p style={{ color: 'var(--text-dim, #94a3b8)', maxWidth: 420, lineHeight: 1.6 }}>
              An unexpected error occurred. Refresh the page to continue. If the issue persists, contact your administrator.
            </p>
          </div>
          {this.state.error && (
            <pre style={{
              background: 'rgba(0,0,0,0.3)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 12,
              padding: '1rem 1.5rem',
              fontSize: '0.8rem',
              color: '#ef4444',
              maxWidth: 600,
              overflow: 'auto',
              textAlign: 'left',
            }}>
              {this.state.error.message}
            </pre>
          )}
          <button
            onClick={() => window.location.reload()}
            style={{
              height: 48,
              padding: '0 2rem',
              background: 'var(--primary, #e11d48)',
              color: 'white',
              border: 'none',
              borderRadius: 12,
              fontWeight: 800,
              fontSize: '0.95rem',
              fontFamily: 'inherit',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
            }}
          >
            <RefreshCcw size={18} />
            Reload Application
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
