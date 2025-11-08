import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

function JobList() {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/jobs/list/')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setJobs(data);
        } else {
          setError(data.error || 'Unexpected response');
        }
      })
      .catch(err => {
        setError("Failed to load jobs: " + err.message);
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 text-dark font-sans py-12 px-6">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-primary mb-8 text-center">🧭 Browse Jobs</h2>

        {error && <p className="text-red-500 mb-6 text-center">❌ {error}</p>}
        {jobs.length === 0 && !error && (
          <p className="text-center text-gray-500">No jobs found.</p>
        )}

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {jobs.map(job => (
            <div
              key={job.id}
              className="bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:border-primary transition"
            >
              <h3 className="text-xl font-bold text-primary mb-1">{job.title}</h3>
              <p className="text-sm text-gray-500 mb-2">📍 {job.location}</p>
              <p className="text-sm text-gray-700 mb-4">
                {job.description.slice(0, 100)}...
              </p>
              <Link
                to={`/jobs/${job.id}`}
                className="inline-block bg-primary text-white px-4 py-2 rounded hover:bg-orange-500 transition"
              >
                🔍 View & Apply
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default JobList;
