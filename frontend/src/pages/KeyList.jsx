import React, { useEffect, useState } from 'react';
import { apikeyApi } from '../lib/api';
import { Key, Plus, Trash2, Shield, RefreshCw, Mail, Phone, User as UserIcon, Edit2 } from 'lucide-react';
import { Link } from 'react-router-dom';

const KeyList = () => {
    const [keys, setKeys] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    const fetchKeys = async (pageNumber) => {
        setLoading(true);
        try {
            const res = await apikeyApi.get(`/?page=${pageNumber}`);
            setKeys(res.data.items);
            setTotalPages(res.data.pages);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchKeys(page);
    }, [page]);

    const toggleKeyStatus = async (id) => {
        try {
            await apikeyApi.patch(`/${id}/toggle`);
            fetchKeys(page);
        } catch (err) {
            alert("Action failed");
        }
    };

    const deleteKey = async (id) => {
        if (!window.confirm("Are you sure you want to delete this key permanently?")) return;
        try {
            await apikeyApi.delete(`/${id}`);
            fetchKeys(page);
        } catch (err) {
            alert("Delete failed");
        }
    };

    const updateRPM = async (id, currentRPM) => {
        const newRPM = window.prompt("Adjust RPM (Requests Per Minute):", currentRPM);
        if (newRPM !== null && !isNaN(newRPM) && newRPM !== "") {
            try {
                await apikeyApi.put(`/${id}`, { rpm: parseInt(newRPM) });
                fetchKeys(page);
            } catch (err) {
                alert("Failed to update RPM");
            }
        }
    };

    return (
        <div className="dashboard-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h2>API Management</h2>
                    <p className="subtitle">Secure keys for external integration</p>
                </div>
                <Link to="/keys/create">
                    <button className="btn-small"><Plus size={18} /> Generate New Key</button>
                </Link>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '3rem' }}>
                    <RefreshCw className="animate-spin" />
                </div>
            ) : (
                <div style={{ overflowX: 'auto' }}>
                    <table className="user-table">
                        <thead>
                            <tr>
                                <th>Key Info</th>
                                <th>Assigned To</th>
                                <th>Limits (RPM)</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {keys.map(k => (
                                <tr key={k.id}>
                                    <td>
                                        <div style={{ fontWeight: '600' }}>{k.key_name}</div>
                                        <code style={{ fontSize: '0.75rem', color: 'var(--primary)' }}>{k.key}</code>
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
                                            <UserIcon size={14} /> {k.key_user_name}
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                                            <Mail size={12} /> {k.contact_email}
                                        </div>
                                    </td>
                                    <td>{k.rpm}</td>
                                    <td>
                                        <span className={`status-dot ${k.is_active ? 'active' : 'inactive'}`}></span>
                                        {k.is_active ? 'Active' : 'Revoked'}
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <button className="icon-btn" onClick={() => updateRPM(k.id, k.rpm)} title="Edit Rate Limit">
                                                <Edit2 size={18} color="var(--primary)" />
                                            </button>
                                            <button className="icon-btn" onClick={() => toggleKeyStatus(k.id)} title={k.is_active ? 'Revoke' : 'Active'}>
                                                <Shield size={18} color={k.is_active ? '#f59e0b' : '#10b981'} />
                                            </button>
                                            <button className="icon-btn" onClick={() => deleteKey(k.id)} title="Delete">
                                                <Trash2 size={18} color="var(--danger)" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                <button 
                    className="btn-secondary" 
                    style={{ width: '100px' }} 
                    disabled={page === 1} 
                    onClick={() => setPage(p => p - 1)}
                >Previous</button>
                <div style={{ display: 'flex', alignItems: 'center', fontWeight: '500' }}>
                    Page {page} of {totalPages}
                </div>
                <button 
                    className="btn-secondary" 
                    style={{ width: '100px' }} 
                    disabled={page === totalPages} 
                    onClick={() => setPage(p => p + 1)}
                >Next</button>
            </div>
        </div>
    );
};

export default KeyList;
