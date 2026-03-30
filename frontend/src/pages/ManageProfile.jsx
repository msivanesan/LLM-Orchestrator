import React, { useState } from 'react';
import { Lock, Loader2, ShieldCheck } from 'lucide-react';
import api from '../lib/api';

const ManageProfile = () => {
    const [passwordData, setPasswordData] = useState({ old_password: '', new_password: '' });
    const [feedback, setFeedback] = useState({ message: '', type: '' });
    const [loading, setLoading] = useState(false);

    const handlePasswordChange = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.post('/change-password', passwordData);
            setFeedback({ message: "Password updated successfully!", type: 'success' });
            setPasswordData({ old_password: '', new_password: '' });
        } catch (err) {
            setFeedback({ message: err.response?.data?.message || "Failed to update password", type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard-card" style={{ maxWidth: '500px' }}>
            <h2>Security Settings</h2>
            <p className="subtitle" style={{ marginBottom: '1.5rem' }}>Update your account password</p>
            
            <form onSubmit={handlePasswordChange}>
                <div className="form-group">
                    <label>Current Password</label>
                    <div className="input-wrapper">
                        <Lock />
                        <input 
                            type="password" 
                            placeholder="Current Password" 
                            required 
                            value={passwordData.old_password}
                            onChange={e => setPasswordData({...passwordData, old_password: e.target.value})} 
                        />
                    </div>
                </div>
                <div className="form-group">
                    <label>New Password</label>
                    <div className="input-wrapper">
                        <ShieldCheck />
                        <input 
                            type="password" 
                            placeholder="New Password" 
                            required 
                            value={passwordData.new_password}
                            onChange={e => setPasswordData({...passwordData, new_password: e.target.value})} 
                        />
                    </div>
                </div>
                <button type="submit" disabled={loading}>
                    {loading ? <Loader2 className="animate-spin" /> : 'Update Password'}
                </button>
                {feedback.message && (
                    <div className={`feedback ${feedback.type}`}>{feedback.message}</div>
                )}
            </form>
        </div>
    );
};

export default ManageProfile;
