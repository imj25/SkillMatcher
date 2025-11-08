import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  const token = localStorage.getItem('access');
  const userType = localStorage.getItem('user_type'); // must be set at login

  return (
    <div className="min-h-screen bg-gray-100 text-dark font-sans">
      <div className="max-w-4xl mx-auto py-12 px-6">
        <h1 className="text-4xl font-bold text-primary mb-8 text-center">Welcome to SKILLMATCHER</h1>
  
        <div className="bg-zinc-100 rounded-xl shadow-md p-8 space-y-8">
          {!token && (
            <div className="text-center space-y-4">
              <h2 className="text-xl font-semibold">👋 I’m new here</h2>
              <div className="flex flex-col md:flex-row justify-center gap-4">
                <Link to="/register" className="bg-primary text-white px-6 py-2 rounded hover:bg-orange-500 transition">
                  👤 Register as Job Seeker
                </Link>
                <Link to="/register" className="bg-primary text-white px-6 py-2 rounded hover:bg-orange-500 transition">
                  🏢 Register as Company
                </Link>
                <Link to="/login" className="bg-gray-200 text-dark px-6 py-2 rounded hover:bg-gray-300 transition">
                  🔑 Login
                </Link>
              </div>
            </div>
          )}
  
          {token && userType === 'job_seeker' && (
            <div className="text-center space-y-4">
              <h2 className="text-xl font-semibold">🎯 Job Seeker Dashboard</h2>
              <div className="flex flex-col md:flex-row justify-center gap-4">
                <Link to="/cv-feedback" className="bg-primary text-white px-6 py-2 rounded hover:bg-orange-500 transition">
                  📄 Get CV Feedback
                </Link>
                <Link to="/jobs" className="bg-indigo-500 text-white px-6 py-2 rounded hover:bg-indigo-600 transition">
                  🔍 Browse Jobs
                </Link>
              </div>
            </div>
          )}
  
          {token && userType === 'company' && (
            <div className="text-center space-y-4">
              <h2 className="text-xl font-semibold">🏢 Company Dashboard</h2>
              <div className="flex flex-col md:flex-row justify-center gap-4">
                <Link to="/post-job" className="bg-primary text-white px-6 py-2 rounded hover:bg-orange-500 transition">
                  ➕ Post a Job
                </Link>
                <Link to="/view-applications" className="bg-gray-200 text-dark px-6 py-2 rounded hover:bg-gray-300 transition">
                  📬 View Applications
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
  
}

export default Home;

