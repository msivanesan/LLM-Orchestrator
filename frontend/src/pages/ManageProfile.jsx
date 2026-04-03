import React, { useState, useEffect } from 'react';
import { 
  Lock, Loader2, ShieldCheck, User, Mail, 
  Shield, Edit2, Save, X, Key, Activity, 
  Fingerprint, Smartphone, Globe
} from 'lucide-react';
import api from '../lib/api';

const ManageProfile = () => {
    const [user, setUser] = useState(null);
    const [passwordData, setPasswordData] = useState({ old_password: '', new_password: '' });
    const [feedback, setFeedback] = useState({ message: '', type: '' });
    const [loading, setLoading] = useState(false);
    const [fetching, setFetching] = useState(true);

    const fetchSession = async () => {
        try {
            const res = await api.get('/me');
            setUser(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setFetching(false);
        }
    };

    useEffect(() => {
        fetchSession();
    }, []);

    const handlePasswordChange = async (e) => {
        e.preventDefault();
        setLoading(true);
        setFeedback({ message: '', type: '' });
        try {
            await api.post('/change-password', passwordData);
            setFeedback({ message: "Security credentials updated successfully.", type: 'success' });
            setPasswordData({ old_password: '', new_password: '' });
        } catch (err) {
            setFeedback({ message: err.response?.data?.message || "Internal Security Breach: Check password complexity.", type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    if (fetching) return (
        <div className="loader-container-full">
            <Loader2 className="animate-spin" size={32} />
            <span>Synchronizing Session...</span>
        </div>
    );

    return (
        <div className="console-workspace-unified">
            {/* 🧭 NAVIGATION HEADER */}
            <header className="unified-console-header-v2">
                <div className="header-nav-main">
                    <div className="settings-icon-ring">
                        <User size={20} color="var(--primary)" />
                    </div>
                    <div className="header-nav-info">
                        <h1>Account Settings</h1>
                        <p className="p-inline-audit">Manage your personal developer profile and security keys.</p>
                    </div>
                </div>
            </header>

            <div className="datagrid-container-v2 scroll-y-auto">
                <div className="modern-saas-form">
                    
                    {/* --- PROFILE OVERVIEW --- */}
                    <section className="form-section-modern">
                        <div className="form-section-info">
                            <h3>Identity Overview</h3>
                            <p>Primary identification and authentication parameters.</p>
                        </div>
                        
                        <div className="form-section-inputs">
                            <div className="readonly-profile-card">
                                <div className="profile-avatar-large">
                                    {user?.username?.charAt(0).toUpperCase()}
                                </div>
                                <div className="profile-details">
                                    <div className="detail-row">
                                        <label>Identifier</label>
                                        <span>{user?.username}</span>
                                    </div>
                                    <div className="detail-row">
                                        <label>Assigned Email</label>
                                        <span>{user?.email}</span>
                                    </div>
                                    <div className="detail-row">
                                        <label>Privilege Tier</label>
                                        <span className={`badge-modern-v2 ${user?.role}`}>
                                            {user?.role?.toUpperCase()}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>

                    <div className="form-divider-modern"></div>

                    {/* --- SECURITY SECTION --- */}
                    <section className="form-section-modern">
                        <div className="form-section-info">
                            <h3>Security & Authentication</h3>
                            <p>Update your master access key to maintain account integrity.</p>
                        </div>

                        <div className="form-section-inputs">
                            <form onSubmit={handlePasswordChange} className="settings-inner-form">
                                <div className="form-row-modern">
                                    <label>Current Security Key</label>
                                    <div className="input-group-modern">
                                        <Fingerprint size={16} className="input-icon-v2" />
                                        <input 
                                            type="password" 
                                            placeholder="••••••••" 
                                            required 
                                            value={passwordData.old_password}
                                            onChange={e => setPasswordData({...passwordData, old_password: e.target.value})} 
                                        />
                                    </div>
                                </div>

                                <div className="form-row-modern">
                                    <label>New Security Key</label>
                                    <div className="input-group-modern">
                                        <Lock size={16} className="input-icon-v2" />
                                        <input 
                                            type="password" 
                                            placeholder="••••••••" 
                                            required 
                                            value={passwordData.new_password}
                                            onChange={e => setPasswordData({...passwordData, new_password: e.target.value})} 
                                        />
                                    </div>
                                    <p className="field-help-text">Strong keys contain 8+ characters with mixed entropy.</p>
                                </div>

                                <button type="submit" className="btn-primary-v2" disabled={loading} style={{ marginTop: '1rem' }}>
                                    {loading ? <Loader2 className="animate-spin" size={18} /> : <ShieldCheck size={18} />}
                                    {loading ? 'MODULATING...' : 'UPDATE SECURITY KEY'}
                                </button>

                                {feedback.message && (
                                    <div className={`notification-banner-modern ${feedback.type}`}>
                                        <Activity size={18} />
                                        <span>{feedback.message}</span>
                                    </div>
                                )}
                            </form>
                        </div>
                    </section>

                    <div className="form-divider-modern"></div>

                    {/* --- PREFERENCES --- */}
                    <section className="form-section-modern">
                      <div className="form-section-info">
                          <h3>System Preferences</h3>
                          <p>Configure regional and operative interface settings.</p>
                      </div>
                      
                      <div className="form-section-inputs">
                          <div className="preference-cluster-modern">
                              <div className="pref-unit">
                                  <Globe size={18} />
                                  <div>
                                      <div className="pref-top">Interface Language</div>
                                      <div className="pref-bot">Digital Standard (English)</div>
                                  </div>
                              </div>
                              <div className="pref-unit" style={{ opacity: 0.6 }}>
                                  <Smartphone size={18} />
                                  <div>
                                      <div className="pref-top" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                        Two-Factor Authentication
                                        <span style={{
                                          fontSize: '0.6rem', fontWeight: 800, letterSpacing: '1px',
                                          background: 'rgba(225,29,72,0.1)', color: 'var(--primary)',
                                          border: '1px solid rgba(225,29,72,0.2)',
                                          borderRadius: 6, padding: '2px 6px', textTransform: 'uppercase'
                                        }}>Coming Soon</span>
                                      </div>
                                      <div className="pref-bot">Available in the next security update</div>
                                  </div>
                              </div>
                          </div>
                      </div>
                    </section>

                </div>
            </div>
        </div>
    );
};

export default ManageProfile;
