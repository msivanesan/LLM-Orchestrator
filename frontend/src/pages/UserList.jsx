import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  UserPlus, Loader2, ToggleRight, ToggleLeft, Search, 
  Mail, Shield, ShieldCheck, 
  Activity, Users as UsersIcon, Trash2, Pencil,
  ChevronLeft, ChevronRight
} from 'lucide-react';
import api from '../lib/api';

const UserList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 });
  
  const navigate = useNavigate();

  const fetchUsers = async (page = 1) => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`/?page=${page}&per_page=10`);
      setUsers(res.data.items || []);
      setPagination({
        page: res.data.page,
        pages: res.data.pages,
        total: res.data.total
      });
    } catch (err) {
      setError('Failed to load users. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { 
    fetchUsers(1);
  }, []);

  const toggleUser = async (u) => {
    try {
      await api.patch(`/${u.id}/toggle`);
      fetchUsers(pagination.page);
    } catch (err) {
      alert(err.response?.data?.message || "Action failed");
    }
  };

  const deleteUser = async (id) => {
    if (!window.confirm("Confirm identity revocation.")) return;
    try {
      await api.delete(`/${id}`);
      fetchUsers(pagination.page);
      setActiveMenu(null);
    } catch (err) {
      alert(err.response?.data?.message || "Deletion failed");
    }
  };

  const filteredUsers = users.filter(u => 
    (u.username || '').toLowerCase().includes(searchTerm.toLowerCase()) || 
    (u.email || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = [
    { label: 'Total Identities', value: pagination.total, icon: <UsersIcon size={14} />, color: 'var(--primary)' },
    // Note: Admins/Active counts reflect current page only (10 users per page)
    { label: 'Admins (this page)', value: users.filter(u => u.role === 'admin').length, icon: <ShieldCheck size={14} />, color: '#6366f1' },
    { label: 'Active (this page)', value: users.filter(u => u.is_active).length, icon: <Activity size={14} />, color: '#10b981' }
  ];

  if (loading && users.length === 0) return (
    <div className="loader-container-full">
      <Loader2 className="animate-spin" size={40} />
      <span>Loading Registry...</span>
    </div>
  );

  if (error) return (
    <div className="loader-container-full">
      <span style={{ color: 'var(--primary)', fontSize: '1rem', fontWeight: 700 }}>{error}</span>
      <button className="btn-primary-console-compact" onClick={() => fetchUsers(pagination.page)}>
        Retry
      </button>
    </div>
  );

  return (
    <div className="console-workspace-unified">
      {/* 🏷️ High-Density Inline Header - EVERYTHING IN ONE LINE */}
      <header className="unified-console-header">
        <div className="header-brand-group">
          <h1 className="h1-compact">Identity Audit</h1>
          <div className="header-sep-mini"></div>
          <p className="p-inline-audit">v{pagination.page}/{pagination.pages} • {pagination.total} Validated</p>
        </div>

        <div className="telemetry-ribbon-inline">
          {stats.map((s, idx) => (
            <div key={idx} className="telemetry-item">
              <div className="telemetry-icon" style={{ color: s.color }}>{s.icon}</div>
              <span className="telemetry-label">{s.label}: </span>
              <span className="telemetry-value">{s.value}</span>
            </div>
          ))}
        </div>

        <Link to="/users/create" className="btn-primary-console-compact">
          <UserPlus size={16} />
          <span>Provision</span>
        </Link>
      </header>

      {/* 💠 Unified Data Canvas */}
      <div className="dashboard-card-modern datagrid-container-unified">
        <div className="datagrid-toolbar-compact">
          <div className="toolbar-search-compact">
            <Search size={16} className="search-icon" />
            <input 
              type="text" 
              placeholder="Search identities..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="table-responsive">
          <table className="console-table">
            <thead>
              <tr>
                <th>Identity Cluster</th>
                <th>Privileges</th>
                <th>Network Status</th>
                <th>Communication</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map(u => (
                <tr key={u.id} className="console-row">
                  <td>
                    <div className="user-cell">
                      <div className="user-avatar-modern">
                        {(u.username || 'U').charAt(0).toUpperCase()}
                        <div className={`avatar-status-pip ${u.is_active ? 'online' : 'offline'}`}></div>
                      </div>
                      <div className="user-info-modern">
                        <span className="username-main">{u.username || 'Unknown'}</span>
                        <div className="user-metadata-sub">
                          <span className="user-id">UID-{String(u.id).padStart(4, '0')}</span>
                          <span className="user-dot-sep">•</span>
                          <span className="user-joined">{new Date(u.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className={`badge-modern ${u.role || 'user'}`}>
                      {(u.role || 'user') === 'admin' ? <ShieldCheck size={12} /> : <Shield size={12} />}
                      {u.role || 'user'}
                    </span>
                  </td>
                  <td>
                    <div className="status-cell-modern">
                      <span className={`status-dot-pulse ${u.is_active ? 'active' : 'inactive'}`}></span>
                      {u.is_active ? 'Authorized' : 'De-provisioned'}
                    </div>
                  </td>
                  <td>
                    <div className="email-link-cell"><Mail size={14} /> {u.email}</div>
                  </td>
                  <td className="text-right">
                    <div className="action-row-modern">
                      <button 
                        onClick={() => toggleUser(u)} 
                        className={`action-btn-console ${u.is_active ? 'success-toggle' : 'off-toggle'}`}
                        title={u.is_active ? 'De-provision Access' : 'Authorize Access'}
                      >
                        {u.is_active ? <ToggleRight size={24} strokeWidth={2.5} /> : <ToggleLeft size={24} strokeWidth={2.5} />}
                      </button>
                      
                      <button 
                        className="action-btn-console edit-btn" 
                        onClick={() => navigate(`/users/edit/${u.id}`)}
                        title="Update Identity"
                      >
                        <Pencil size={24} strokeWidth={2.5} />
                      </button>

                      <button 
                        className="action-btn-console delete-btn" 
                        onClick={() => deleteUser(u.id)}
                        title="Revoke Access"
                      >
                        <Trash2 size={24} strokeWidth={2.5} />
                      </button>
                    </div>



                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <footer className="pagination-footer-console">
          <div className="pagination-info">
            Records <span>{(pagination.page-1)*10 + 1}-{Math.min(pagination.page*10, pagination.total)}</span> of <span>{pagination.total}</span>
          </div>
          <div className="pagination-nav">
            <button disabled={pagination.page <= 1} onClick={() => fetchUsers(pagination.page - 1)}>
              <ChevronLeft size={18} />
            </button>
            <div className="page-indices">
              {[...Array(pagination.pages)].map((_, i) => (
                <button 
                  key={i + 1} 
                  className={pagination.page === i + 1 ? 'active' : ''}
                  onClick={() => fetchUsers(i + 1)}
                >
                  {i + 1}
                </button>
              ))}
            </div>
            <button disabled={pagination.page >= pagination.pages} onClick={() => fetchUsers(pagination.page + 1)}>
              <ChevronRight size={18} />
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default UserList;
