import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Mail, Lock } from 'lucide-react';
import api from '../lib/api';

const CreateUser = () => {
  const [formData, setFormData] = useState({ username: '', email: '', password: '', role: 'user' });
  const [feedback, setFeedback] = useState({ message: '', type: '' });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/register', formData);
      setFeedback({ message: "User created successfully!", type: 'success' });
      setTimeout(() => navigate('/users'), 1500);
    } catch (err) {
      setFeedback({ message: err.response?.data?.message || "Failed to create user", type: 'error' });
    }
  };

  return (
    <div className="dashboard-card" style={{ maxWidth: '500px' }}>
      <h2>Create New User</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username</label>
          <div className="input-wrapper">
            <User />
            <input type="text" required onChange={e => setFormData({...formData, username: e.target.value})} />
          </div>
        </div>
        <div className="form-group">
          <label>Email</label>
          <div className="input-wrapper">
            <Mail />
            <input type="email" required onChange={e => setFormData({...formData, email: e.target.value})} />
          </div>
        </div>
        <div className="form-group">
          <label>Password</label>
          <div className="input-wrapper">
            <Lock />
            <input type="password" required onChange={e => setFormData({...formData, password: e.target.value})} />
          </div>
        </div>
        <div className="form-group">
          <label>Role</label>
          <select value={formData.role} onChange={e => setFormData({...formData, role: e.target.value})} className="custom-select">
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <button type="submit">Create User</button>
        {feedback.message && <div className={`feedback ${feedback.type}`}>{feedback.message}</div>}
      </form>
    </div>
  );
};

export default CreateUser;
