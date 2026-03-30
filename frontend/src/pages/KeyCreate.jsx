import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apikeyApi } from '../lib/api';
import { Plus, User, Mail, Phone, Settings, ShieldAlert, Loader2 } from 'lucide-react';

const KeyCreate = () => {
    const [formData, setFormData] = useState({ 
        key_name: '', 
        key_user_name: '', 
        contact_email: '', 
        contact_phone: '', 
        rpm: 60 
    });
    const [loading, setLoading] = useState(false);
    const [feedback, setFeedback] = useState({ message: '', type: '' });
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setFeedback({ message: '', type: '' });
        try {
            await apikeyApi.post('/create', formData);
            setFeedback({ message: 'API Key generated successfully and notification sent to user!', type: 'success' });
            setTimeout(() => navigate('/keys'), 2000);
        } catch (err) {
            setFeedback({ message: err.response?.data?.message || 'Generation failed', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard-card" style={{ maxWidth: '600px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
                <ShieldAlert color="var(--primary)" size={32} />
                <div>
                    <h2>Generate API Key</h2>
                    <p className="subtitle">Securely issue external keys for integration</p>
                </div>
            </div>

            <form onSubmit={handleSubmit}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    <div className="form-group">
                        <label>Key Name (e.g., Billing Project)</label>
                        <div className="input-wrapper">
                            <Settings />
                            <input 
                                type="text" 
                                placeholder="Key Name" 
                                required 
                                value={formData.key_name}
                                onChange={e => setFormData({ ...formData, key_name: e.target.value })} 
                            />
                        </div>
                    </div>
                    <div className="form-group">
                        <label>RPM Limit (Requests per min)</label>
                        <div className="input-wrapper">
                            <Settings />
                            <input 
                                type="number" 
                                placeholder="60" 
                                required 
                                value={formData.rpm}
                                onChange={e => setFormData({ ...formData, rpm: parseInt(e.target.value) })} 
                            />
                        </div>
                    </div>
                </div>

                <div className="form-group">
                    <label>Assigned User/Company Name</label>
                    <div className="input-wrapper">
                        <User />
                        <input 
                            type="text" 
                            placeholder="Full Name" 
                            required 
                            value={formData.key_user_name}
                            onChange={e => setFormData({ ...formData, key_user_name: e.target.value })} 
                        />
                    </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    <div className="form-group">
                        <label>Contact Email (For notifications)</label>
                        <div className="input-wrapper">
                            <Mail />
                            <input 
                                type="email" 
                                placeholder="email@example.com" 
                                required 
                                value={formData.contact_email}
                                onChange={e => setFormData({ ...formData, contact_email: e.target.value })} 
                            />
                        </div>
                    </div>
                    <div className="form-group">
                        <label>Contact Phone (Optional)</label>
                        <div className="input-wrapper">
                            <Phone />
                            <input 
                                type="text" 
                                placeholder="+1 234 567 890" 
                                value={formData.contact_phone}
                                onChange={e => setFormData({ ...formData, contact_phone: e.target.value })} 
                            />
                        </div>
                    </div>
                </div>

                <div style={{ marginTop: '2rem' }}>
                    <button type="submit" disabled={loading}>
                        {loading ? <Loader2 className="animate-spin" /> : 'Confirm & Generate Key'}
                    </button>
                    <button type="button" className="btn-secondary" style={{ marginTop: '1rem' }} onClick={() => navigate('/keys')}>Cancel</button>
                </div>

                {feedback.message && (
                    <div className={`feedback ${feedback.type}`}>{feedback.message}</div>
                )}
            </form>
        </div>
    );
};

export default KeyCreate;
