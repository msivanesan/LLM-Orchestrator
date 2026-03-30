import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Loader2, Key } from 'lucide-react';
import api from '../lib/api';

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [feedback, setFeedback] = useState({ message: '', type: '' });
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleForgotPassword = async (e) => {
        e.preventDefault();
        
        // Basic Client-side Validation (Production Grade)
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setFeedback({ message: 'Please enter a valid email address.', type: 'error' });
            return;
        }

        setLoading(true);
        setFeedback({ message: '', type: '' });
        try {
            const res = await api.post('/forgot-password', { email });
            sessionStorage.setItem('forgot_email', email);
            setFeedback({ message: 'A secure link has been sent to your inbox.', type: 'success' });
            setTimeout(() => navigate('/verify-otp'), 2000);
        } catch (err) {
            setFeedback({ message: err.response?.data?.message || 'We could not process your request. Please try again.', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
                <div style={{ display: 'inline-flex', padding: '1rem', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '16px', marginBottom: '1.5rem' }}>
                    <Key size={32} color="#6366f1" />
                </div>
                <h1 style={{ fontSize: '1.75rem', fontWeight: '800', letterSpacing: '-0.02em' }}>Identity Recovery</h1>
                <p className="subtitle" style={{ fontSize: '1rem', color: 'var(--text-dim)' }}>Verification code will be sent to your secure inbox.</p>
            </div>
            
            <form onSubmit={handleForgotPassword} noValidate>
                <div className="form-group">
                    <label style={{ fontWeight: '500' }}>Registered Email</label>
                    <div className="input-wrapper">
                        <Mail size={18} />
                        <input 
                            type="email" 
                            placeholder="Enter your email" 
                            required 
                            autoComplete="email"
                            value={email}
                            onChange={e => setEmail(e.target.value)} 
                        />
                    </div>
                </div>
                <button type="submit" disabled={loading} style={{ height: '3.5rem', fontSize: '1rem' }}>
                    {loading ? <Loader2 className="animate-spin" /> : 'Request Reset Code'}
                </button>
                <Link to="/login" className="btn-secondary" style={{ marginTop: '1.25rem', display: 'flex', alignItems: 'center', justifyContent: 'center', textDecoration: 'none', height: '3.5rem' }}>
                    Cancel & Return
                </Link>
                {feedback.message && (
                    <div className={`feedback ${feedback.type}`} aria-live="polite">
                        {feedback.message}
                    </div>
                )}
            </form>
        </div>
    );
};

export default ForgotPassword;
