import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { UserPlus, Loader2, ToggleRight, ToggleLeft } from 'lucide-react';
import api from '../lib/api';

const UserList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = async () => {
    try {
      const res = await api.get('/');
      setUsers(res.data.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsers(); }, []);

  const toggleUser = async (id) => {
    try {
      await api.patch(`/${id}/toggle`);
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.message || "Action failed");
    }
  };

  if (loading) return <div className="loader"><Loader2 className="animate-spin" /> Fetching Users...</div>;

  return (
    <div className="dashboard-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2>User Management</h2>
        <Link to="/users/create" className="btn-small"><UserPlus size={16} /> New User</Link>
      </div>
      <table className="user-table">
        <thead>
          <tr>
            <th>User</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map(u => (
            <tr key={u.id}>
              <td>{u.username}</td>
              <td>{u.email}</td>
              <td><span className={`badge ${u.role}`}>{u.role}</span></td>
              <td>
                <span className={`status-dot ${u.is_active ? 'active' : 'inactive'}`}></span>
                {u.is_active ? 'Active' : 'Disabled'}
              </td>
              <td>
                <button onClick={() => toggleUser(u.id)} className="icon-btn">
                  {u.is_active ? <ToggleRight color="#4ade80" /> : <ToggleLeft color="#94a3b8" />}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserList;
