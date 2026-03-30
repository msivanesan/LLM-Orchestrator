import React from 'react';

const DashboardHome = ({ user }) => {
  if (!user) return null;
  
  return (
    <div className="dashboard-card">
      <h2>Dashboard Overview</h2>
      <p>Welcome back, <strong>{user.username}</strong>.</p>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Role</h3>
          <p>{user.role}</p>
        </div>
        <div className="stat-card">
          <h3>Status</h3>
          <p style={{ color: user.is_active ? '#4ade80' : '#f87171' }}>
            {user.is_active ? 'Active' : 'Disabled'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default DashboardHome;
