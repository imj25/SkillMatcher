import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Register() {
  const [userType, setUserType] = useState('job_seeker');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch('http://127.0.0.1:8000/api/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, user_type: userType,email }),
    });

    const data = await response.json();

    if (response.ok) {
      setMessage('✅ Registration successful! Redirecting...');
      setTimeout(() => navigate('/login'), 1500);
    } else {
      setMessage('❌ ' + (data.error || JSON.stringify(data)));
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 text-dark flex items-center justify-center font-sans">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold text-center text-primary mb-6">📝 Register for SKILLMATCHER</h2>

        {message && <p className="mb-4 text-sm text-red-600 text-center">{message}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">👤 Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
          </div>
          <div>
            <label className="block text-sm mb-1">📧 Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
          </div>
          <div>
            <label className="block text-sm mb-1">🔒 Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
          </div>
          <div>
            <label className="block text-sm mb-1">🧭 Select Role</label>
            <select
              value={userType}
              onChange={(e) => setUserType(e.target.value)}
              className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="job_seeker">Job Seeker</option>
              <option value="company">Company</option>
            </select>
          </div>
          <button type="submit" className="w-full bg-primary text-white py-2 rounded hover:bg-orange-500 transition">
            Register
          </button>
        </form>
      </div>
    </div>
  );
}

export default Register;
