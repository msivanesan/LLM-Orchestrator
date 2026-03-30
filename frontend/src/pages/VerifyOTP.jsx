import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { CheckCircle, Lock, Loader2, ShieldAlert, ShieldCheck } from 'lucide-react';
import api from '../lib/api';

const VerifyOTP = () => {
    const [email, setEmail] = useState('');
    const [formData, setFormData] = useState({ otp: '', newPassword: '' });
    const [feedback, setFeedback] = useState({ message: '', type: '' });
    const [loading, setLoading] = useState(false);
    const [timer, setTimer] = useState(60); 
    const navigate = useNavigate();

    useEffect(() => {
        const storedEmail = sessionStorage.getItem('forgot_email');
        if (!storedEmail) {
            navigate('/forgot-password');
        } else {
            setEmail(storedEmail);
        }
    }, [navigate]);

    useEffect(() => {
        let interval;
        if (timer > 0) {
            interval = setInterval(() => setTimer(prev => prev - 1), 1000);
        }
        return () => clearInterval(interval);
    }, [timer]);

    const handleResendOTP = async () => {
        if (timer > 0) return;
        setLoading(true);
        try {
            await api.post('/forgot-password', { email });
            setFeedback({ message: "New OTP sent!", type: 'success' });
            setTimer(60);
        } catch (err) {
            setFeedback({ message: err.response?.data?.message || 'Failed to resend', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleResetPassword = async (e) => {
        e.preventDefault();
        
        if (formData.otp.length !== 6) {
            setFeedback({ message: 'The security code must be 6 digits.', type: 'error' });
            return;
        }

        setLoading(true);
        try {
            await api.post('/verify-otp', { 
                email, 
                otp: formData.otp, 
                new_password: formData.newPassword 
            });
            setFeedback({ message: "Security credentials updated! Redirecting to login...", type: 'success' });
            sessionStorage.removeItem('forgot_email');
            setTimeout(() => navigate('/login'), 2500);
        } catch (err) {
            setFeedback({ message: err.response?.data?.message || 'Verification failed. Please check the code.', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container" style={{ maxWidth: '460px' }}>
            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                <div style={{ display: 'inline-flex', padding: '1rem', background: 'rgba(52, 211, 153, 0.1)', borderRadius: '16px', marginBottom: '1.5rem' }}>
                    <ShieldCheck size={32} color="#10b981" />
                </div>
                <h1 style={{ fontSize: '1.75rem', fontWeight: '800' }}>Secure Verification</h1>
                <p className="subtitle">We've sent a 6-digit code to <b>{email}</b></p>
            </div>
            
            <form onSubmit={handleResetPassword} noValidate>
                <div className="form-group">
                    <label style={{ fontWeight: '500' }}>One-Time Passcode</label>
                    <div className="input-wrapper">
                        <CheckCircle size={18} />
                        <input 
                            type="text" 
                            placeholder="••••••" 
                            maxLength="6" 
                            required 
                            autoFocus
                            style={{ letterSpacing: '4px', fontWeight: '700' }}
                            value={formData.otp}
                            onChange={e => setFormData({...formData, otp: e.target.value.replace(/\D/g,'')})} 
                        />
                    </div>
                </div>
                <div className="form-group">
                    <label style={{ fontWeight: '500' }}>New Secure Password</label>
                    <div className="input-wrapper">
                        <Lock size={18} />
                        <input 
                            type="password" 
                            placeholder="Min 8 characters" 
                            required 
                            autoComplete="new-password"
                            value={formData.newPassword}
                            onChange={e => setFormData({...formData, newPassword: e.target.value})} 
                        />
                    </div>
                </div>
                
                <button type="submit" disabled={loading} style={{ height: '3.5rem' }}>
                    {loading ? <Loader2 className="animate-spin" /> : 'Confirm & Reset'}
                </button>
                
                <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                    <button 
                        type="button" 
                        className="btn-secondary" 
                        disabled={timer > 0 || loading} 
                        onClick={handleResendOTP}
                        style={{ flex: 1, padding: '0.75rem', fontSize: '0.875rem' }}
                    >
                        {timer > 0 ? `Retry in ${timer}s` : 'Resend Code'}
                    </button>
                    <Link to="/forgot-password" style={{ flex: 1, textDecoration: 'none' }}>
                        <button type="button" className="btn-secondary" style={{ width: '100%', padding: '0.75rem', fontSize: '0.875rem' }}>Wrong Email?</button>
                    </Link>
                </div>
                
                {feedback.message && (
                    <div className={`feedback ${feedback.type}`} style={{ marginTop: '1.5rem' }} aria-live="assertive">
                        {feedback.message}
                    </div>
                )}
            </form>
        </div>
    );
};

export default VerifyOTP;
