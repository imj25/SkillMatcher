import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Navbar() {
  const token = localStorage.getItem('access');
  const userType = localStorage.getItem('user_type');
  const navigate = useNavigate();

  const handleLogout = () => {
    ['access', 'refresh', 'user_type'].forEach(k => localStorage.removeItem(k));
    navigate('/');
    window.location.reload();
  };

  return (
    <nav className="bg-[#121212] text-white flex items-center justify-between px-6 py-4 shadow-md">
      <Link to="/" className="text-2xl font-bold text-primary tracking-wide">SKILLMATCHER</Link>

      <div className="flex items-center gap-4 text-sm">
        {/* Not logged in */}
        {!token && (
          <>
            <Link to="/login" className="hover:text-orange-400 transition">Login</Link>
            <Link to="/register" className="hover:text-orange-400 transition">Register</Link>
          </>
        )}

        {/* Job Seeker Links */}
        {token && userType === 'job_seeker' && (
          <>
            <Link to="/" className="hover:text-orange-400 transition">Dashboard</Link>
            <Link to="/jobs" className="hover:text-orange-400 transition">Browse Jobs</Link>
            <Link to="/cv-feedback" className="hover:text-orange-400 transition">CV Feedback</Link>
            <Link to="/profile" className="hover:text-orange-400 transition">Profile</Link>
            <button onClick={handleLogout} className="text-red-400 hover:text-red-300 transition">Logout</button>
          </>
        )}

        {/* Company Links */}
        {token && userType === 'company' && (
          <>
            <Link to="/" className="hover:text-orange-400 transition">Dashboard</Link>
            <Link to="/post-job" className="hover:text-orange-400 transition">Post Job</Link>
            <Link to="/view-applications" className="hover:text-orange-400 transition">Applications</Link>
            <Link to="/profile" className="hover:text-orange-400 transition">👤 Profile</Link>
            <button onClick={handleLogout} className="text-red-400 hover:text-red-300 transition">Logout</button>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;

